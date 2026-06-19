import asyncio
from tools.registry import register

@register("run_shell")
async def run_shell(command: str) -> str:
    """执行shell命令，返回输出"""
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        if stdout:
            return stdout.decode()
        if stderr:
            return f"stderr: {stderr.decode()}"
        return "执行完成，无输出"
    except asyncio.TimeoutError:
        return "执行超时"
    except Exception as e:
        return f"执行失败: {e}"