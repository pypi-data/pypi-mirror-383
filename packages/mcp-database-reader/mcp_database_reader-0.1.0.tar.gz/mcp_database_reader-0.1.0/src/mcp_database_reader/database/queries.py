from typing import List, Dict, Any, Optional
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession

class QueryExecutor:
    def __init__(self, connector):
        self.connector = connector
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行SQL查询"""
        if not query.strip().upper().startswith(('SELECT', 'SHOW', 'DESC', 'DESCRIBE')):
            return [{"error": "只允许执行查询语句 (SELECT, SHOW, DESC 等)"}]
        
        try:
            async with AsyncSession(self.connector.engine) as session:
                result = await session.execute(text(query), params or {})
                
                # 将结果转换为字典列表
                columns = result.keys()
                rows = result.fetchall()
                
                return [
                    {column: value for column, value in zip(columns, row)}
                    for row in rows
                ]
        except Exception as e:
            return [{"error": f"查询执行错误: {str(e)}"}]
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        try:
            async with AsyncSession(self.connector.engine) as session:
                if self.connector.db_type in ["mysql", "postgresql"]:
                    result = await session.execute(text("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """), {"table_name": table_name})
                else:  # sqlite
                    result = await session.execute(text(
                        f"PRAGMA table_info({table_name})"
                    ))
                
                schema_info = result.fetchall()
                return {
                    "table_name": table_name,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == 'YES' if len(col) > 2 else not col[3],
                            "default": col[3] if len(col) > 3 else None
                        } for col in schema_info
                    ]
                }
        except Exception as e:
            return {"error": f"获取表结构失败: {str(e)}"}
    
    async def list_tables(self) -> List[str]:
        """列出所有表"""
        try:
            async with AsyncSession(self.connector.engine) as session:
                if self.connector.db_type in ["mysql", "postgresql"]:
                    if self.connector.db_type == "mysql":
                        query = """
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = DATABASE()
                        """
                    else:  # postgresql
                        query = """
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public'
                        """
                    result = await session.execute(text(query))
                else:  # sqlite
                    result = await session.execute(text("""
                        SELECT name as table_name 
                        FROM sqlite_master 
                        WHERE type='table'
                    """))
                
                tables = result.fetchall()
                return [table[0] for table in tables if table[0] not in ['alembic_version', 'sqlite_sequence']]
        except Exception as e:
            print(f"获取表列表错误: {e}")
            return []