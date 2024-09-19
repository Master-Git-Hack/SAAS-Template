from typing import Any, Dict, List, Optional, Tuple
from warnings import catch_warnings, simplefilter

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.schema import MetaData

from .. import config


class InstanceDB:
    BASE = None
    URIS = {}
    ENGINES = {}
    SESSIONS = {}

    def __new__(cls):
        cls.BASE = declarative_base()
        names = config.SECRETS.get("DB_NAMES", [])
        cls.URIS = {name: f"{config.PSQL_URI}/{name}" for name in names}
        cls.ENGINES = {name: create_engine(cls.URIS[name]) for name in names}
        cls.SESSIONS = {
            name: sessionmaker(
                autocommit=False, autoflush=False, bind=cls.ENGINES[name]
            )
            for name in names
        }
        return super().__new__(cls)

    def get_db(self, db_name: str = "catastro_v2") -> Session:
        __Current = self.SESSIONS[db_name]()
        try:
            return __Current
        finally:
            __Current.close()

    def valuaciones(
        self,
    ) -> Session:
        __Current = self.SESSIONS["valuaciones"]()
        try:
            yield __Current
        finally:
            __Current.close()

    def catastro_v2(
        self,
    ) -> Session:
        __Current = self.SESSIONS["catastro_v2"]()
        try:
            yield __Current
        finally:
            __Current.close()

    def fotogrametria(self) -> Session:
        __Current = self.SESSIONS["fotogrametria"]()
        try:
            yield __Current
        finally:
            __Current.close()

    def execute_query(self, db_name: str, query: str):
        engine = self.ENGINES.get(db_name)
        if engine:
            with engine.connect() as connection:
                result = connection.execute(text(query))
                return result.fetchall()
        else:
            raise ValueError(f"Database '{db_name}' not found.")

    def inspect_all_schemas(self, db_name: str = "valuaciones"):
        return [
            {
                "label": schema,
                "code": code,
                "items": [
                    {"label": table.replace(f"{schema}.", ""), "parent": schema}
                    for table in self.inspect_me(db_name=db_name, schema=schema)
                ],
            }
            for code, schema in enumerate(self.get_all_schemas(db_name))
        ]

    def get_all_schemas(self, db_name: str = "valuaciones") -> list:
        engine = self.ENGINES[db_name]
        with engine.connect() as connection:
            sql = "SELECT schema_name FROM information_schema.schemata;"
            result = connection.execute(text(sql))
            return [row[0] for row in result.fetchall()]

    def inspect_me(self, db_name: str, schema: str = "valuaciones"):
        with catch_warnings():
            simplefilter("ignore", category=SAWarning)
            engine = self.ENGINES[db_name]
            meta = MetaData()
            meta.reflect(bind=engine, schema=schema)
        return meta.tables.keys()


class Template:
    Model: object = None
    schema = None
    Current: Optional[object] = None

    def __init__(
        self,
        Model,
        Schema,
        db: Session,
    ) -> None:
        self.Model = Model
        self.db = db
        self.Schema = Schema
        self.__check_attr()

    def __check_attr(self):
        if self.Model is None:
            logger.debug("----------> Model is not defined:\n")
            return False
        return True

    def __enter__(self):
        if self.__check_attr():
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Model = None
        self.schema = None
        self.Current = None

    def __call__(self) -> Any:
        return self.Current

    def get(self, id: int, dict: bool = False, **kwargs) -> Optional[object]:
        """
        Get a record by id
        Args:
            id (int): The id of the record
            dict (bool): Whether to return a dictionary or an object
            exclude (list): List of fields to exclude
        Returns:
            object: The record
        """
        self.__check_attr()
        try:
            self.Current = self.db.query(self.Model).get(id)
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.Current = None
        if dict:
            return self.dict(**kwargs)
        return self.Current

    def filter(
        self, dict: bool = False, excludes: Optional[List[str]] = None, **kwargs
    ) -> Optional[object]:
        """
        Filter records
        Args:
            kwargs (dict): Keywords arguments
        Returns:
            object: The record
        """
        self.__check_attr()
        try:
            self.Current = self.db.query(self.Model).filter_by(**kwargs).one_or_none()
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.Current = None
        if dict:
            return self.dict(excludes=excludes)
        return self.Current

    def get_first(
        self, dict: bool = False, excludes: Optional[List[str]] = None, **kwargs
    ):
        self.__check_attr()
        try:
            self.Current = (
                self.db.query(self.Model)
                .filter_by(**kwargs)
                .order_by(self.Model.id.asc())
                .one_or_none()
            )
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.Current = None
        if dict:
            return self.dict(excludes=excludes)
        return self.Current

    def get_last(
        self, dict: bool = False, excludes: Optional[List[str]] = None, **kwargs
    ):
        self.__check_attr()
        try:
            self.Current = (
                self.db.query(self.Model)
                .filter_by(**kwargs)
                .order_by(self.Model.id.desc())
                .one_or_none()
            )
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.Current = None

        if dict:
            return self.dict(excludes=excludes)
        return self.Current

    def filter_group(
        self, list: bool = False, excludes: Optional[List[str]] = None, **kwargs
    ) -> Optional[object]:
        """
        Filter records
        Args:
            kwargs (dict): Keywords arguments
        Returns:
            object: The record
        """
        self.__check_attr()

        self.Current = self.db.query(self.Model).filter_by(**kwargs).all()

        if list or exclude is not None and len(exclude) > 0:
            return self.list(excludes=excludes)
        return self.Current

    def filter_raw(self, **kwargs):
        self.__check_attr()
        try:
            return self.db.query(self.Model).filter(**kwargs)
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            return None

    def all(
        self,
        list: bool = False,
        excludes: Optional[List[str]] = None,
    ) -> Optional[object]:
        """
        Get all records
        Returns:
            object: The record
        """
        self.__check_attr()

        self.Current = self.db.query(self.Model).all()

        if list:
            return self.list(excludes=excludes)
        return self.Current

    def create(
        self, dict: bool = False, excludes: Optional[List[str]] = None, **kwargs
    ) -> Optional[object]:
        """
        Create a record
        Args:
            kwargs (dict): Keywords arguments
        Returns:
            object: The record
        """
        self.__check_attr()

        self.Current = self.Model(**kwargs)
        try:
            self.db.add(self.Current)
            self.db.commit()
            self.db.refresh(self.Current)
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.db.rollback()

            return None
        else:
            if dict:
                return self.dict(excludes=excludes)
            return self.Current

    def update(
        self,
        id: Optional[int] = None,
        dict: bool = False,
        excludes: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[object]:
        """
        Update a record
        Args:
            id (int): The id of the record
            kwargs (dict): Keywords arguments
        Returns:
            object: The record
        """
        self.__check_attr()

        if id is not None:
            self.Current = self.db.query(self.Model).get(id)
        for key, value in kwargs.items():
            setattr(self.Current, key, value)
        try:
            self.db.merge(self.Current)
            self.db.commit()
            self.db.refresh(self.Current)

        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.db.rollback()

            return None
        else:
            if dict:
                self.dict(excludes=excludes)
            return self.Current

    def delete(self, id: Optional[int] = None) -> None:
        """
        Delete a record
        Args:
            id (int): The id of the record
        Returns:
            None
        """
        self.__check_attr()

        if id is not None:
            self.Current = self.db.query(self.Model).get(id)
        if self.Current is None:
            return None
        try:
            self.db.delete(self.Current)
            self.db.commit()
            self.Current = None
            return self.Current
        except Exception as e:
            print(f"----------> Unexpected error:\n {str(e)}")
            self.db.rollback()
            return self.Current

    def dict(
        self,
        data: Optional[object] = None,
        excludes: Optional[List[str]] = None,
    ) -> Dict:
        self.__check_attr()
        if data is not None:
            self.Current = data
        if self.Current is None:
            return {}
        if self.Schema is None:
            values = {
                key: value
                for key, value in vars(data).items()
                if not key.startswith("_")
            }
            if excludes is not None:
                for key in excludes:
                    values.pop(key, None)
            return values
        schema = self.Schema.from_orm(data)
        return schema.dict()

    def list(
        self,
        data: Optional[object] = None,
        **kwargs,
    ) -> List:
        self.__check_attr()
        if data is not None:
            self.Current = data
        if self.Current is None:
            return []

        return [
            self.dict(
                data=record,
                **kwargs,
            )
            for record in self.Current
        ]
