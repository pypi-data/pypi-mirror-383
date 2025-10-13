# coding: utf-8
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text, insert, delete, select, Connection
from .models import BaseTables, Path, System, EnvVar, NotificationData
from .utils import get_value

class BaseAsyncLocalDatabase:
    
     def __init__(self, app_name: str, path : str, is_new_database : bool, insistent_tables : list[str]):
          self._app_name = app_name
          self.is_new_database = is_new_database
          self.insistent_tables = insistent_tables
          self._engine: AsyncEngine = create_async_engine(f'sqlite+aiosqlite:///{path}')

     @property
     def engine(self):
          return self._engine

     @property
     def app_name(self):
          return self._app_name
     
     async def close(self):
        await self._engine.dispose()  
        self._engine.pool.dispose()  
        self._engine = None

     async def init_db(self):
          async with self.engine.begin() as conn:
               await conn.run_sync(BaseTables.meta_data.create_all)
               await conn.execute(BaseTables.system.insert().values(App=self.app_name, Tema='light'))
               await conn.commit()

     async def select(self, table: str, where: str = None, conn : Connection = None):
          if not conn:
               async with self.engine.connect() as conn:
                    query = f"SELECT * FROM {table} WHERE App = :app_name"
                    if where:
                         query += f" AND {where}"
                    result = await conn.execute(text(query), {'app_name': self.app_name})
                    return [row._mapping for row in result]
          else:
               query = f"SELECT * FROM {table} WHERE App = :app_name"
               if where:
                    query += f" AND {where}"
               result = await conn.execute(text(query), {'app_name': self.app_name})
               return [row._mapping for row in result]

     async def get_path(self, name):
          name = get_value(name)
          data = await self.select('path', f"Name = '{name}'")
          return Path(data[0]).Path if data else None

     async def update_path(self, name: str, path_name: str):
          name, path_name = get_value(name), get_value(path_name)
          exists_path = await self.get_path(name)
          async with self.engine.begin() as conn:
               if exists_path:
                    await conn.execute(
                         BaseTables.path.update().where(
                         (BaseTables.path.c.Name == name) & (BaseTables.path.c.App == self.app_name)
                         ).values(Path=path_name)
                    )
               else:
                    await conn.execute(BaseTables.path.insert().values(App=self.app_name, Name=name, Path=path_name))

     async def delete_path(self, name: str):
          name = get_value(name)
          async with self.engine.begin() as conn:
               await conn.execute(
                    BaseTables.path.delete().where(
                         (BaseTables.path.c.Name == name) & (BaseTables.path.c.App == self.app_name)
                    )
               )

     async def get_var(self, name):
          name = get_value(name)
          data = await self.select('env_var', f"Name = '{name}'")
          return EnvVar(data[0]).Value if data else None

     async def update_var(self, name: str, value: str):
          name, value = get_value(name), get_value(value)
          exists_var = await self.get_var(name)
          async with self.engine.begin() as conn:
               if exists_var:
                    await conn.execute(
                         BaseTables.env_var.update().where(
                         (BaseTables.env_var.c.Name == name) & (BaseTables.env_var.c.App == self.app_name)
                         ).values(Value=value)
                    )
               else:
                    await conn.execute(BaseTables.env_var.insert().values(App=self.app_name, Name=name, Value=value))

     async def delete_var(self, name: str):
          name = get_value(name)
          async with self.engine.begin() as conn:
               await conn.execute(
                    BaseTables.env_var.delete().where(
                         (BaseTables.env_var.c.Name == name) & (BaseTables.env_var.c.App == self.app_name)
                    )
               )

     async def get_theme(self):
          data = await self.select('system')
          if data:
               return System(data[0]).Theme
          async with self.engine.begin() as conn:
               await conn.execute(BaseTables.system.insert().values(App=self.app_name, Tema='light'))
          return 'light'

     async def update_theme(self, theme: str):
          theme = get_value(theme)
          async with self.engine.begin() as conn:
               await conn.execute(
                    BaseTables.system.update().where(BaseTables.system.c.App == self.app_name).values(Tema=theme)
               )

     async def insert_notification(self, data: NotificationData):
          async with self.engine.begin() as conn:
               ins = insert(BaseTables.notification).values(
                    App=self.app_name,
                    guid=data.guid,
                    local=data.local,
                    title=data.title,
                    message=data.message,
                    type=data.type,
                    date=data.date
               )
               await conn.execute(ins)

     async def delete_notification(self, guid: str):
          async with self.engine.begin() as conn:
               stmt = delete(BaseTables.notification).where(
                    (BaseTables.notification.c.guid == guid) & (BaseTables.notification.c.App == self.app_name)
               )
               await conn.execute(stmt)

     async def clear_notification(self):
          async with self.engine.begin() as conn:
               stmt = delete(BaseTables.notification).where(BaseTables.notification.c.App == self.app_name)
               await conn.execute(stmt)

     async def get_notifications(self):
          async with self.engine.connect() as conn:
               stmt = select(BaseTables.notification).where(BaseTables.notification.c.App == self.app_name)
               result = await conn.execute(stmt)
               notifications = result.fetchall()
               return [NotificationData(**notification._mapping) for notification in notifications]

     async def insert_notification(self, data : NotificationData):
          async with self.engine.connect() as conn:
               ins = insert(BaseTables.notification).values(App=self.app_name, guid=data.guid, local=data.local, title=data.title, message=data.message, type=data.type,date=data.date)
               await conn.execute(ins)
               await conn.commit()

     async def delete_notification(self, guid : str):
          async with self.engine.connect() as conn:
               await conn.execute(delete(BaseTables.notification).where((BaseTables.notification.c.guid == guid) & (BaseTables.notification.c.App == self.app_name)))
               await conn.commit()

     async def clear_notification(self):
          async with self.engine.connect() as conn:
               await conn.execute(delete(BaseTables.notification).where(BaseTables.notification.c.App == self.app_name))
               await conn.commit()

     async def get_notifications(self):
          notifications = await self.select('notification')
          return [NotificationData(**notification) for notification in notifications]