#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("❌ 请安装 MCP: pip install 'mcp[cli]'")
    sys.exit(1)

print("当前目录:", os.getcwd())
from .database.connector import DatabaseConnector
from .database.queries import QueryExecutor

# 创建 FastMCP 实例
mcp = FastMCP("Database Reader")

# 初始化数据库连接
db_connector = DatabaseConnector()
query_executor = None

async def initialize_database():
    """初始化数据库连接"""
    global query_executor
    await db_connector.initialize()
    query_executor = QueryExecutor(db_connector)
    
    if not await db_connector.test_connection():
        raise Exception("数据库连接失败")

@mcp.tool()
async def execute_sql_query(sql_query: str) -> str:
    """执行SQL查询语句"""
    if not query_executor:
        await initialize_database()
    
    result = await query_executor.execute_query(sql_query)
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_table_structure(table_name: str) -> str:
    """获取数据表的结构信息"""
    if not query_executor:
        await initialize_database()
    
    schema = await query_executor.get_table_schema(table_name)
    
    if "error" in schema:
        return f"错误: {schema['error']}"
    
    output = f"表 '{table_name}' 的结构:\n\n"
    for column in schema["columns"]:
        nullable = "是" if column["nullable"] else "否"
        default = column["default"] or "无"
        output += f"• {column['name']}: {column['type']} (可空: {nullable}, 默认值: {default})\n"
    
    return output

@mcp.tool()
async def list_database_tables() -> str:
    """列出数据库中的所有数据表"""
    if not query_executor:
        await initialize_database()
    
    tables = await query_executor.list_tables()
    
    if not tables:
        return "数据库中没有找到任何表"
    
    return f"数据库中的表 ({len(tables)} 个):\n\n" + "\n".join([f"• {table}" for table in tables])

@mcp.tool()
async def query_table_data(table_name: str, limit: int = 10) -> str:
    """查询表中的数据样本"""
    if not query_executor:
        await initialize_database()
    
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    result = await query_executor.execute_query(query)
    
    if result and "error" in result[0]:
        return f"错误: {result[0]['error']}"
    
    return json.dumps({
        "table": table_name,
        "count": len(result),
        "data": result
    }, ensure_ascii=False, indent=2)

def main():
    """主函数 - 使用同步方式运行"""
    print("🚀 启动 MCP 数据库读取服务器...", file=sys.stderr)
    
    try:
        # 使用 mcp.run() 而不是 await mcp.run()
        mcp.run(transport="stdio")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()  # 直接调用同步函数，不使用 asyncio.run()