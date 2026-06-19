import aiofiles
from tools.registry import register

@register("read_file")
async def read_file(path: str) -> str:
    """读取本地文件内容"""
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return await f.read()
    except Exception as e:
        return f"读取失败: {e}"

@register("write_file")
async def write_file(path: str, content: str) -> str:
    """写入内容到本地文件"""
    try:
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(content)
        return f"写入成功: {path}"
    except Exception as e:
        return f"写入失败: {e}"