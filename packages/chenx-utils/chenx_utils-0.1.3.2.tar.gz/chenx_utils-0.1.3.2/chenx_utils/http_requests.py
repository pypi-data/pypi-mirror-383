import json
import asyncio
import ssl
from typing import Any, Dict, Optional, Union
import aiohttp
from aiohttp import FormData, ClientTimeout
import os 
from .data.response_json import CODES, CustomException  # 复用项目自定义异常
import logging as logger


class AsyncHttpClient:
    """异步HTTP客户端（单例模式），封装常用HTTP方法及文件处理"""
    _instance: Optional['AsyncHttpClient'] = None
    _lock: asyncio.Lock = asyncio.Lock()  # 异步锁保证多协程安全
    session: Optional[aiohttp.ClientSession] = None
    ssl_context: Optional[ssl.SSLContext] = None

    # 禁止外部直接实例化
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    # 禁止重复初始化
    def __init__(self, verify_ssl: bool = True, ssl_context: Optional[ssl.SSLContext] = None):
        if hasattr(self, '_initialized'):
            return
        
        # 优先使用自定义SSL上下文，否则根据verify_ssl创建
        self.ssl_context = ssl_context or (ssl.create_default_context() if verify_ssl else None)
        self._initialized = True  # 标记初始化完成
        logger.debug("AsyncHttpClient 初始化完成")

    # 异步初始化会话（确保会话唯一且可重用）
    async def _init_session(self):
        """延迟初始化会话，避免过早创建资源"""
        if not self.session or self.session.closed:
            # 关键修复：verify_ssl=False 时，强制 connector 的 ssl=False
            if self.ssl_context is None:  # 对应 verify_ssl=False 的情况
                connector = aiohttp.TCPConnector(ssl=False)  # 彻底禁用 SSL 验证
            else:
                connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=60)
            )
            logger.debug(f"HTTP会话创建成功（SSL验证: {self.ssl_context is not None}）")

    # 获取单例实例（线程/协程安全）
    @classmethod
    async def get_instance(
        cls, 
        verify_ssl: bool = False, 
        ssl_context: Optional[ssl.SSLContext] = None
    ) -> 'AsyncHttpClient':
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls(verify_ssl=verify_ssl, ssl_context=ssl_context)
            await cls._instance._init_session()  # 确保会话已初始化
        return cls._instance

    # 通用响应处理（标准化错误格式）
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """统一处理响应，转换为项目标准格式"""
        try:
            # 尝试解析JSON响应（兼容项目自定义响应结构）
            response_data = await response.json()
        except json.JSONDecodeError:
            # 非JSON响应（如二进制文件）直接返回内容
            return {"status": response.status, "content": await response.text()}

        # 处理错误状态码（复用项目CustomException）
        if not (200 <= response.status < 300):
            error_msg = response_data.get("message", f"请求失败（{response.status}）")
            logger.error(f"HTTP错误: {error_msg}")
            raise CustomException(
                code=CODES.HTTP_REQUEST_ERROR,
                message=error_msg,
                http_status=response.status
            )
        
        logger.debug(f"响应数据: {response_data}")
        return response_data

    # 通用请求发送（减少代码冗余）
    async def _request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        data: Optional[Union[Dict[str, Any], FormData]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[ClientTimeout] = None
    ) -> Dict[str, Any]:
        """通用请求方法，支持所有HTTP方法"""
        await self._init_session()
        headers = headers or {}
        timeout = timeout or ClientTimeout(total=60)  # 方法级超时（覆盖全局）

        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not isinstance(data, FormData) else None,  # FormData需用data参数
                data=data if isinstance(data, FormData) else None,
                params=params,
                timeout=timeout
            ) as response:
                return await self._handle_response(response)
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP客户端错误: {str(e)}")
            raise CustomException(
                code=CODES.HTTP_CLIENT_ERROR,
                message=f"请求失败: {str(e)}"
            ) from e
        except CustomException:
            raise  # 直接抛出项目自定义异常
        except Exception as e:
            logger.error(f"请求处理异常: {str(e)}")
            raise CustomException(
                code=CODES.INTERNAL_ERROR,
                message=f"内部处理错误: {str(e)}"
            ) from e

    # 封装HTTP方法（复用通用请求）
    async def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.debug(f"GET请求: {url}, 参数: {params}")
        return await self._request(
            method="GET",
            url=url,
            headers=headers,
            params=params
        )

    async def post(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        data: Optional[Union[Dict[str, Any], FormData]] = None,
        timeout: Optional[ClientTimeout] = None
    ) -> Dict[str, Any]:
        logger.debug(f"POST请求: {url}, 数据: {data}")
        return await self._request(
            method="POST",
            url=url,
            headers=headers,
            data=data,
            timeout=timeout
        )

    async def put(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.debug(f"PUT请求: {url}, 数据: {data}")
        return await self._request(
            method="PUT",
            url=url,
            headers=headers,
            data=data
        )

    async def delete(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.debug(f"DELETE请求: {url}, 数据: {data}")
        return await self._request(
            method="DELETE",
            url=url,
            headers=headers,
            data=data
        )

    # 文件下载（优化资源流处理）
    async def download_file(
        self, 
        url: str, 
        save_path: str, 
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """下载文件并保存（优化大文件流式处理）"""
        await self._init_session()
        try:
            async with self.session.get(url, headers=headers, timeout=ClientTimeout(total=300)) as response:
                if not (200 <= response.status < 300):
                    raise CustomException(
                        code=CODES.HTTP_REQUEST_ERROR,
                        message=f"下载失败（{response.status}）: {await response.text()}"
                    )
                
                # 流式写入文件（适合大文件）
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                
                logger.debug(f"文件保存成功: {save_path}")
                return save_path
        
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            # 清理失败的文件
            if os.path.exists(save_path):
                os.remove(save_path)
            raise
    async def request_with_file(self, url, headers: Dict[str, str] = None, data: Dict[str, Any] = None) -> Any:
        """
        上传文件到指定 URL
        :param url: 上传的目标 URL
        :param file_path: 文件路径
        :param headers: 可选的请求头
        :param extra_data: 可选的额外表单数据
        :return: 响应数据
        """
        await self._init_session()

        try:
             # 如果传入的是 FormData，直接使用
            # 获取 FormData 对象
            form = data.get('file') if isinstance(data.get('file'), aiohttp.FormData) else None
            
            if not form:
                # 如果没有提供 FormData，创建新的
                form = aiohttp.FormData()
                if data:
                    for key, value in data.items():
                        if value is not None:
                            form.add_field(key, str(value))
            logger.debug(f"form: {form}")
            async with self.session.request(
                "post", 
                url, 
                data=form, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                return await self._handle_response(response)
            
        except aiohttp.ClientError as e:
            logger.error(f"Upload failed: {str(e)}")
            raise aiohttp.ClientError(e)
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise Exception(f"Unexpected error during upload: {str(e)}")
       
    # 文件上传（统一表单处理）
    async def upload_file(
        self, 
        url: str, 
        form_data: FormData, 
        headers: Optional[Dict[str, str]] = None,
        timeout: ClientTimeout = ClientTimeout(total=300)
    ) -> Dict[str, Any]:
        """上传文件（支持FormData表单）"""
        if not isinstance(form_data, FormData):
            raise CustomException(
                code=CODES.INVALID_PARAM,
                message="上传数据必须是aiohttp.FormData类型"
            )
        logger.debug(f"文件上传请求: {url}")
        return await self._request(
            method="POST",
            url=url,
            headers=headers,
            data=form_data,
            timeout=timeout
        )

    # Base64数据上传（简化接口）
    async def upload_base64(
        self, 
        url: str, 
        base64_str: str, 
        headers: Optional[Dict[str, str]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """上传Base64编码数据（自动封装为FormData）"""
        form_data = FormData()
        form_data.add_field("file", base64_str, content_type="text/plain")
        
        if extra_data:
            for key, value in extra_data.items():
                form_data.add_field(key, str(value))
        
        return await self.upload_file(
            url=url,
            form_data=form_data,
            headers=headers
        )

    # 资源清理（确保会话关闭）
    async def close(self):
        """关闭HTTP会话（程序退出时调用）"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.debug("HTTP会话已关闭")

    # 上下文管理器支持（自动关闭资源）
    async def __aenter__(self):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
