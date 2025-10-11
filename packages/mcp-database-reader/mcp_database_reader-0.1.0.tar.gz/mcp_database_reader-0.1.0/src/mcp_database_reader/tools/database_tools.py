from typing import List, Dict, Any
import mcp
import mcp.types as types
import json

class DatabaseTools:
    def __init__(self, query_executor):
        self.query_executor = query_executor
    
    @mcp.tool()
    async def execute_sql_query(self, sql_query: str) -> str:
        """执行SQL查询语句
        
        Args:
            sql_query: 要执行的SQL查询语句 (仅支持SELECT、SHOW等查询操作)
            
        Returns:
            查询结果的JSON字符串
        """
        result = await self.query_executor.execute_query(sql_query)
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    @mcp.tool()
    async def get_table_structure(self, table_name: str) -> str:
        """获取数据表的结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构的详细描述
        """
        schema = await self.query_executor.get_table_schema(table_name)
        
        if "error" in schema:
            return f"错误: {schema['error']}"
        
        output = f"表 '{table_name}' 的结构:\n\n"
        for column in schema["columns"]:
            nullable = "是" if column["nullable"] else "否"
            default = column["default"] or "无"
            output += f"• {column['name']}: {column['type']} (可空: {nullable}, 默认值: {default})\n"
        
        return output
    
    @mcp.tool()
    async def list_database_tables(self) -> str:
        """列出数据库中的所有数据表
        
        Returns:
            数据库中的表列表
        """
        tables = await self.query_executor.list_tables()
        
        if not tables:
            return "数据库中没有找到任何表"
        
        return f"数据库中的表 ({len(tables)} 个):\n\n" + "\n".join([f"• {table}" for table in tables])
    
    @mcp.tool()
    async def query_table_data(self, table_name: str, limit: int = 10) -> str:
        """查询表中的数据样本
        
        Args:
            table_name: 表名
            limit: 返回的记录数量 (默认: 10)
            
        Returns:
            表数据的JSON格式
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        result = await self.query_executor.execute_query(query)
        
        if result and "error" in result[0]:
            return f"错误: {result[0]['error']}"
        
        return json.dumps({
            "table": table_name,
            "count": len(result),
            "data": result
        }, ensure_ascii=False, indent=2)