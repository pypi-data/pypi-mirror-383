"""
x_dm_python - Twitter DM 批量并发发送库的 Python 类型存根

此文件为 PyCharm/VSCode 等 IDE 提供精确的类型提示
"""
from typing import Optional

__version__: str

class DMResult:
    """
    单条私信发送结果

    Attributes:
        success: 是否发送成功
        user_id: 目标用户ID
        message: 发送的消息内容
        error_msg: 错误信息（成功时为空）
        http_status: HTTP 状态码
        event_id: Twitter 事件ID（成功时返回）
    """
    success: bool
    user_id: str
    message: str
    error_msg: str
    http_status: int
    event_id: Optional[str]

    def __init__(
        self,
        success: bool = False,
        user_id: str = "",
        message: str = "",
        error_msg: str = "",
        http_status: int = 0,
        event_id: Optional[str] = None,
    ) -> None: ...

    def __repr__(self) -> str: ...

class BatchDMResult:
    """
    批量私信发送结果

    Attributes:
        success_count: 成功发送的数量
        failure_count: 失败发送的数量
        results: 每条私信的详细结果
    """
    success_count: int
    failure_count: int
    results: list[DMResult]

    def __init__(
        self,
        success_count: int = 0,
        failure_count: int = 0,
        results: list[DMResult] = [],
    ) -> None: ...

    def __repr__(self) -> str: ...

class Twitter:
    """
    Twitter 客户端

    提供异步的私信发送功能。所有发送方法都是异步的，需要使用 await 调用。

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

            # 批量发送
            user_ids = ["123456789", "987654321"]
            batch_result = await client.send_batch_direct_messages(user_ids, "Hello everyone!")
            print(f"成功: {batch_result.success_count}, 失败: {batch_result.failure_count}")

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        cookies: str,
        proxy_url: Optional[str] = None,
        _logger_name: str = "twitter_dm",
    ) -> None:
        """
        创建 Twitter 客户端

        Args:
            cookies: Twitter 账号的 cookies 字符串，必须包含 ct0, auth_token, twid
            proxy_url: 可选的代理服务器 URL (格式: http://host:port 或 socks5://host:port)
            _logger_name: 日志记录器名称（保留参数，供兼容使用）

        Raises:
            RuntimeError: 当 cookies 格式无效或缺少必需字段时

        Example:
            ```python
            cookies = "ct0=abc123; auth_token=xyz789; twid=u%3D123456789"
            client = x_dm_python.Twitter(cookies)

            # 使用代理
            client_with_proxy = x_dm_python.Twitter(
                cookies,
                proxy_url="http://127.0.0.1:7890"
            )
            ```
        """
        ...

    async def send_direct_message(
        self,
        user_id: str,
        message: str,
    ) -> DMResult:
        """
        发送单条私信（异步方法）

        Args:
            user_id: 目标用户ID（纯数字字符串）
            message: 消息内容（最大 10000 字符）

        Returns:
            DMResult: 发送结果，包含成功状态、错误信息等

        Raises:
            RuntimeError: 当发送失败时（网络错误、认证失败等）

        Example:
            ```python
            result = await client.send_direct_message("123456789", "你好！")
            if result.success:
                print(f"发送成功，事件ID: {result.event_id}")
            else:
                print(f"发送失败: {result.error_msg}")
            ```
        """
        ...

    async def send_batch_direct_messages(
        self,
        user_ids: list[str],
        message: str,
        client_transaction_ids: Optional[list[str]] = None,
    ) -> BatchDMResult:
        """
        批量发送私信（异步方法，并发执行）

        同时向多个用户发送相同的消息，使用并发执行提高效率。

        Args:
            user_ids: 目标用户ID列表（纯数字字符串）
            message: 消息内容（最大 10000 字符）
            client_transaction_ids: 可选的客户端事务ID列表（用于去重）

        Returns:
            BatchDMResult: 批量发送结果，包含成功/失败数量和每条消息的详细结果

        Raises:
            RuntimeError: 当批量发送失败时

        Example:
            ```python
            user_ids = ["123456789", "987654321", "555666777"]
            result = await client.send_batch_direct_messages(user_ids, "群发消息")

            print(f"成功: {result.success_count}, 失败: {result.failure_count}")
            for dm_result in result.results:
                if not dm_result.success:
                    print(f"用户 {dm_result.user_id} 发送失败: {dm_result.error_msg}")
            ```
        """
        ...

    def get_cookies(self) -> str:
        """
        获取当前 cookies 字符串

        Returns:
            str: 完整的 cookies 字符串

        Example:
            ```python
            cookies = client.get_cookies()
            print(cookies)
            ```
        """
        ...

    def validate_cookies(self) -> bool:
        """
        验证 cookies 是否有效

        检查 cookies 是否包含必需的认证信息（ct0, auth_token, user_id）

        Returns:
            bool: True 表示 cookies 有效，False 表示无效

        Example:
            ```python
            if client.validate_cookies():
                print("Cookies 有效")
            else:
                print("Cookies 无效或已过期")
            ```
        """
        ...
