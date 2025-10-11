import os
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import StaticPool
import aiosqlite

class DatabaseConnector:
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.db_type: str = "sqlite"
    
    async def initialize(self) -> None:
        """初始化数据库连接"""
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        if self.db_type == "mysql":
            connection_string = self._get_mysql_connection_string()
        elif self.db_type == "postgresql":
            connection_string = self._get_postgresql_connection_string()
        else:  # sqlite
            connection_string = self._get_sqlite_connection_string()
        
        # 创建异步引擎
        if self.db_type == "sqlite":
            self.engine = create_async_engine(
                connection_string,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_async_engine(connection_string)
        
        print(f"✅ 数据库连接已建立: {self.db_type}")
    
    def _get_mysql_connection_string(self) -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "test")
        
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
    
    def _get_postgresql_connection_string(self) -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "test")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    def _get_sqlite_connection_string(self) -> str:
        db_path = os.getenv("DB_PATH", "./example.db")
        return f"sqlite+aiosqlite:///{db_path}"
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return False