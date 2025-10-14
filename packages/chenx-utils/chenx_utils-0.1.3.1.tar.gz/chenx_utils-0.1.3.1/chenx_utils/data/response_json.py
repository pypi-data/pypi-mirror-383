
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse



from enum import Enum, unique
ERROR_CODE = 1
SUCCESS_CODE = 0

@unique
class CODES(Enum):
    """
    业务错误码与 HTTP 状态码的映射
    格式：(业务错误码, 默认消息, 推荐 HTTP 状态码)
    """
    
    # ==================================
    # 成功（HTTP 2xx）
    # ==================================
    SUCCESS = (0, "请求成功", 200)
    
    # ==================================
    # 客户端错误（HTTP 4xx）
    # ==================================
    # 新增：参数无效（对应 HTTP 400）
    INVALID_PARAM = (4000, "参数无效（格式错误或值超出范围）", 400)
    PARAM_ERROR = (4001, "参数格式错误（如缺少必填字段）", 400)
    INVALID_PROMPT = (4002, "输入提示词无效（为空或不符合规范）", 400)
    FILE_FORMAT_ERROR = (4003, "文件格式错误（仅支持 PNG/JPG）", 400)
    
    # 401 Unauthorized：未授权
    PERMISSION_DENIED = (4011, "未登录或令牌过期", 401)
    
    # 403 Forbidden：权限不足
    NO_ACCESS = (4031, "没有操作权限", 403)
    
    # 404 Not Found：资源不存在
    RESOURCE_NOT_FOUND = (4041, "请求的资源不存在", 404)
    TASK_NOT_FOUND = (4042, "任务 ID 不存在", 404)
    
    # ==================================
    # 服务器错误（HTTP 5xx）
    # ==================================
    # 500 Internal Server Error：服务器内部错误
    INTERNAL_ERROR = (5001, "系统内部错误（如数据库异常）", 500)
    GENERATION_FAILED = (5002, "3D 模型生成失败", 500)
    FILE_IO_ERROR = (5003, "文件读写失败（如磁盘满）", 500)
    
    # 502 Bad Gateway：第三方服务错误
    # 新增：HTTP 请求错误（如服务器返回非 2xx 状态码，对应 HTTP 502）
    # 新增：HTTP 客户端错误（如连接失败、DNS 解析错误，对应 HTTP 400）
    HTTP_REQUEST_ERROR = (5020, "服务请求失败（如上游服务异常、网关错误）", 502)
    THIRD_PARTY_ERROR = (5021, "第三方服务响应异常（如模型服务超时）", 502)
    HUGGINGFACE_ERROR = (5022, "Hugging Face 接口调用失败", 502)
    RAY_SERVE_ERROR = (5023, "Ray Serve 服务未响应", 502)
    HTTP_CLIENT_ERROR = (5024, "客户端请求失败（如网络中断、连接超时）", 502)
    SERVER_ERROR = (5025, "服务端发生错误", 502)
    
    # 503 Service Unavailable：服务暂时不可用
    RESOURCE_EXHAUSTED = (5031, "GPU 资源耗尽，请稍后再试", 503)
    TASK_LIMITED = (5032, "任务数量超限，请稍后提交", 503)
    
    def __init__(self, code: int, message: str, http_status: int):
        self.code = code          # 业务错误码
        self.message = message    # 默认错误消息
        self.http_status = http_status  # 对应的 HTTP 状态码
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message} (HTTP {self.http_status})"
    




# 自定义异常
class CustomException(Exception):
    def __init__(
        self,
        code: CODES,  # 传入 CODES 枚举
        message: str = None,  # 可选：覆盖默认消息
        http_status: int = None  # 可选：覆盖推荐的 HTTP 状态码
    ):
        self.code = code.code
        self.message = message or code.message
        self.http_status = http_status or code.http_status  # 优先使用传入的 HTTP 状态码
        super().__init__(self.message)


def error_response(message = None, data = None, code: CODES = CODES.SERVER_ERROR,  status_code: int = None):
    message = code.message if message is None else message
    if isinstance(data, BaseModel):
        data = data.model_dump()
    return JSONResponse(
                {
                "code": status_code if status_code else ERROR_CODE,
                "message": message,
                "data": data
            },
            code.http_status
    )

def json_response(message = None, data = None, code: CODES  = CODES.SUCCESS, status_code: int = None):
    message = code.message if message is None else message
    if isinstance(data, BaseModel):
        data = data.model_dump()
    return JSONResponse(
            {
                "code": status_code if status_code else SUCCESS_CODE,
                "message": message,
                "data": data
            },
            code.http_status
    )
