# coding: utf-8
from sqlalchemy import create_engine, inspect, text, insert
from sqlalchemy.engine import Engine
from tempfile import gettempdir
from os import path, makedirs
from .models import BaseTables
from .utils import is_valid_name, get_value
from typing import TypeVar
T = TypeVar('T')

class DataBaseInstall(object):
    
     def __init__(self, app_name : str, *, tables : BaseTables = None, path_local_database = gettempdir(), database_name="MyLocalDatabase", database_folder_name = "MyApp"):
          app_name = get_value(app_name)
          if not database_name.endswith('.db'):
               database_name = f'{database_name}.db'
          if not is_valid_name(app_name):
               app_name = "my_app"
          self._app_name = app_name
          self._path_database = path.join(path_local_database,database_folder_name, database_name)
          self.tables = tables if tables else BaseTables
          self._engine : Engine = None
          self.new_database = not path.isfile(self._path_database)
          self.insistent_tables = []
          if not path.isfile(self._path_database):
               if not path.exists(path.join(path_local_database,database_folder_name)):
                    makedirs(path.join(path_local_database,database_folder_name))

               with self.engine.connect() as conn:
                    conn.execute(text("PRAGMA encoding = 'UTF-8'"))
                    conn.commit()

               
               with self.engine.connect() as conn:
                    self.tables.meta_data.create_all(self.engine)
                    if hasattr(self.tables, 'system'):
                         try:
                              ins = insert(self.tables.system).values(App=app_name, Tema='light')
                              conn.execute(ins)
                              conn.commit()
                         except:
                              ...
          else:
               if not self.are_tables_existing(self.engine):
                    try:
                         self.tables.meta_data.create_all(self.engine)
                    except:
                         ...
               else:
                    try:
                         self.synchronize_columns(self.engine)
                    except:
                         ...

     def instance(self, obj : T) -> T:
          return obj(self._app_name, self._path_database, self.new_database, self.insistent_tables)

     @property
     def engine(self):
          if not self._engine:
               self._engine = create_engine(f'sqlite:///{self._path_database}')
          return self._engine

     def are_columns_existing(self, engine):
          inspector = inspect(engine)
          existing_tables = inspector.get_table_names()
          required_tables = self.tables.meta_data.tables.keys()
          for table_name in required_tables:
               if table_name in existing_tables:
                    existing_columns = inspector.get_columns(table_name)
                    existing_column_names = [column['name'] for column in existing_columns]
                    required_columns = self.tables.meta_data.tables[table_name].c.keys()
                    if not all(column in existing_column_names for column in required_columns):
                         return False
               else:
                    return False
          return True

     def are_tables_existing(self, engine):
          inspector = inspect(engine)
          existing_tables = inspector.get_table_names()
          required_tables = self.tables.meta_data.tables.keys()
          self.insistent_tables = [table for table in required_tables if table not in existing_tables]
          return not bool(self.insistent_tables)

     def synchronize_columns(self, engine):
          inspector = inspect(engine)
          existing_tables = inspector.get_table_names()
          for table_name in self.tables.meta_data.tables.keys():
               if table_name in existing_tables:
                    existing_columns = inspector.get_columns(table_name)
                    existing_column_names = [column['name'] for column in existing_columns]
                    required_columns = self.tables.meta_data.tables[table_name].c.keys()
                    required_column_defs = {col.name: col for col in self.tables.meta_data.tables[table_name].columns}
                    for column in required_columns:
                         if column not in existing_column_names:
                              column_type = required_column_defs[column].type
                              add_column_sql = f'ALTER TABLE {table_name} ADD COLUMN {column} {column_type}'
                              with engine.connect() as conn:
                                   conn.execute(text(add_column_sql))