"""
x_dm_python - Twitter DM 批量并发发送库

提供完全异步的 Python 接口，基于 Rust 实现的高性能 Twitter 私信发送库。

Example:
    ```python
    import asyncio
    import x_dm_python

    async def main():
        cookies = "ct0=xxx; auth_token=yyy; twid=u%3D123456789"
        client = x_dm_python.Twitter(cookies)

        # 发送单条私信
        result = await client.send_direct_message("123456789", "Hello!")
        print(f"成功: {result.success}")

    asyncio.run(main())
    ```
"""

from .x_dm_python import Twitter, DMResult, BatchDMResult, __version__

__all__ = ["Twitter", "DMResult", "BatchDMResult", "__version__"]
