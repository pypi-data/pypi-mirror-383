# coding: utf-8
from sqlalchemy import create_engine, text, insert, delete, update, Connection
from .models import BaseTables, Path, System, EnvVar, NotificationData
from .utils import get_value

class BaseLocalDatabase(object):

    def __init__(self, app_name : str, path : str, is_new_database : bool, insistent_tables : list[str]):
        self._app_name = app_name
        self.is_new_database = is_new_database
        self.insistent_tables = insistent_tables
        self._engine = create_engine(f'sqlite:///{path}')
        
    @property
    def engine(self):
        return self._engine

    @property
    def app_name(self):
        return self._app_name
    
    def close(self):
        self._engine.dispose()  
        self._engine.pool.dispose()  
        self._engine = None
 
    def select(self, table : str, where : str = None, conn : Connection = None):
        if not conn:
            with self.engine.connect() as conn:
                if where:
                    query = conn.execute(text(f"select * from {table} where App = '{self.app_name}' and {where}"))
                else:
                    query = conn.execute(text(f"select * from {table} where App = '{self.app_name}'"))
                data = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                return data
        else:
            if where:
                query = conn.execute(text(f"select * from {table} where App = '{self.app_name}' and {where}"))
            else:
                query = conn.execute(text(f"select * from {table} where App = '{self.app_name}'"))
            data = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
            return data

    def get_path(self, name):
        name = get_value(name)
        data = self.select('path', f"Name = '{name}'")
        for d in data:
            return Path(d).Path

    def update_path(self, name : str, path_name : str):
        name = get_value(name)
        path_name = get_value(path_name)
        existsPath = self.get_path(name)

        with self.engine.connect() as conn:
            if existsPath != None:
                stmt = update(BaseTables.path).where(
                    (BaseTables.path.c.Name == name) &
                    (BaseTables.path.c.App == self.app_name)
                ).values(Path=path_name)
                conn.execute(stmt)
            else:
                ins = insert(BaseTables.path).values(App=self.app_name, Name=name, Path=path_name)
                conn.execute(ins)
            conn.commit()

    def delete_path(self, name : str):
        name = get_value(name)
        with self.engine.connect() as conn:
            stmt = delete(BaseTables.path).where((BaseTables.path.c.Name == name) & (BaseTables.env_var.c.App == self.app_name))
            conn.execute(stmt)
            conn.commit()

    def get_var(self, name):
        name = get_value(name)
        data = self.select('env_var', f"name = '{name}'")
        for d in data:
            return EnvVar(d).Value

    def update_var(self, name : str, value : str):
        name = get_value(name)
        value = get_value(value)
        existsVar = self.get_var(name)
        with self.engine.connect() as conn:
            if existsVar != None:
               stmt = update(BaseTables.env_var).where(
                    (BaseTables.env_var.c.Name == name) &
                    (BaseTables.env_var.c.App == self.app_name)
               ).values(Value=value)
               conn.execute(stmt)
            else:
               ins = insert(BaseTables.env_var).values(App=self.app_name, Name=name, Value=value)
               conn.execute(ins)
            conn.commit()

    def delete_var(self, name : str):
        name = get_value(name)
        with self.engine.connect() as conn:
            stmt = delete(BaseTables.env_var).where((BaseTables.env_var.c.Name == name) & (BaseTables.env_var.c.App == self.app_name))
            conn.execute(stmt)
            conn.commit()

    def get_theme(self):
        data = self.select('system')
        if data:
            return System(data[0]).Theme
        else:
            with self.engine.connect() as conn:
                ins = insert(BaseTables.system).values(App=self.app_name, Tema='light')
                conn.execute(ins)
                conn.commit()
            return 'light'

    def update_theme(self, theme : str):
        theme = get_value(theme)
        _theme = self.get_theme()
        if _theme:
            with self.engine.connect() as conn:
                stmt = update(BaseTables.system).where(
                    BaseTables.system.c.App == self.app_name
                ).values(Tema=theme)
                conn.execute(stmt)
                conn.commit()

    def insert_notification(self, data : NotificationData):
        with self.engine.connect() as conn:
            ins = insert(BaseTables.notification).values(App=self.app_name, guid=data.guid, local=data.local, title=data.title, message=data.message, type=data.type,date=data.date)
            conn.execute(ins)
            conn.commit()

    def delete_notification(self, guid : str):
        with self.engine.connect() as conn:
            conn.execute(delete(BaseTables.notification).where((BaseTables.notification.c.guid == guid) & (BaseTables.notification.c.App == self.app_name)))
            conn.commit()

    def clear_notification(self):
        with self.engine.connect() as conn:
            conn.execute(delete(BaseTables.notification).where(BaseTables.notification.c.App == self.app_name))
            conn.commit()

    def get_notifications(self):
        notifications = self.select('notification')
        return [NotificationData(**notification) for notification in notifications]
           

    




