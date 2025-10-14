import httpx
from mcp.server import FastMCP

# # 初始化 FastMCP 服务器
app = FastMCP('res-return')


@app.tool()
async def res_return() -> str:
    """
    返回一个固定的字符串
    
    Returns:
        字符串 "hello"
    """
    return "hello"
    

if __name__ == "__main__":
    app.run(transport='stdio')


