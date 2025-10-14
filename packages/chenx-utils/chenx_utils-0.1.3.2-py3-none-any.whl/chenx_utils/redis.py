import json
from typing import Optional
from redis.asyncio import Redis, RedisCluster, ConnectionError
from .data.config import MODE, REDIS_PORT, REDIS_HOST, REDIS_PASSWORD, TASK_STATUS_PREFIX, TASK_QUEUE_KEY, TASK_DATA_PREFIX
from redis.cluster import ClusterNode
import logging as logger
# TASK_QUEUE_KEY = "img_task_queue"
# TASK_DATA_PREFIX = "img_task_data:"
# TASK_IMG_URL_PREFIX = "img_url:"

def singleton(cls):
    """单例装饰器"""
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

@singleton
class RedisManager:
    def __init__(self):
        self.redis_client = None

    def _create_client(self):
        """创建 Redis 客户端"""
        if MODE == "Production":
           cluster_nodes = [ClusterNode(host=REDIS_HOST, port=REDIS_PORT)]
           self.redis_client = RedisCluster(startup_nodes=cluster_nodes, decode_responses=True,password=REDIS_PASSWORD, health_check_interval=30)
        else:
            self.redis_client = Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                retry_on_timeout=True,
                password=REDIS_PASSWORD,
                health_check_interval=30
            )
    async def ensure_connection(self):
        """确保 Redis 连接可用"""
        """确保 Redis 集群连接可用"""
        if self.redis_client is None:
            self._create_client()
        try:
            # 检查集群状态
            if hasattr(self.redis_client, 'cluster_info'):
                # 如果是集群模式，使用 cluster_info() 检查集群健康状态
                cluster_info = await self.redis_client.cluster_info()
                if cluster_info.get('cluster_state') != 'ok':
                    raise ConnectionError("Redis cluster is not in a healthy state")
            else:
                # 如果是单节点模式，使用 ping() 检查连接
                await self.redis_client.ping()
                # print("connect success")
        except (ConnectionError, Exception) as e:
            logger.error(f"Redis connection error: {e}")
            # 如果连接失败，重新创建客户端
            self._create_client()
            try:
                # 重新检查连接
                if hasattr(self.redis_client, 'cluster_info'):
                    cluster_info = await self.redis_client.cluster_info()
                    if cluster_info.get('cluster_state') != 'ok':
                        raise ConnectionError("Redis cluster reconnection failed: cluster is not healthy")
                else:
                    await self.redis_client.ping()
            except Exception as e:
                logger.error(f"Redis reconnection failed: {e}")
                raise Exception("Redis reconnection failed")
        except Exception as e:
            raise Exception(f"Redis reconnection failed: {e}")


    async def set_task_status(self, task_id: str, status: str = "processing", progress: any = None, result: str = None, timestamp: str = None, ttl: int = 172800):
        """设置任务状态，默认1小时过期"""
        key = f"{TASK_STATUS_PREFIX}{task_id}"
        # print(f"set_task_status: {result} and progress is {progress}")
        try:
            await self.ensure_connection()
            mapping = {}
            if status:
                # 如果是枚举类型，转换为字符串
                mapping["status"] = str(status.value) if hasattr(status, 'value') else str(status)
            # 如果 progress 是字典，需要序列化
            if progress:
                if isinstance(progress, dict):
                    mapping["progress"] = int(progress)
                else:
                    mapping["progress"] = int(progress)
            if result is not None:  # 使用 is not None 来允许空列表
                # 如果是列表或字典，转换为 JSON 字符串
                if isinstance(result, (list, dict)):
                    mapping["output"] = json.dumps(result,  ensure_ascii=False)
                else:
                    mapping["output"] = result  # 其他类型转字符串
            if timestamp:
                mapping["created_at"] = int(timestamp)
            # print(f"mapping: {mapping}")
            # print(f"mapping type: {type(mapping)}")
            await self.redis_client.hset(key, mapping=mapping)
            res = await self.redis_client.hgetall(key)
            await self.redis_client.expire(key, ttl)
        except Exception as e:
            # await self.connect()
            logger.error(e)
            # print(f"Input types - status: {type(mapping["status"])}, progress: {type(mapping["progress"])}, result: {type(mapping["outputs"])}")
            raise Exception("set_task_status error")

    async def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        key = f"{TASK_STATUS_PREFIX}{task_id}"
        try:
            await self.ensure_connection()
            res = await self.redis_client.hgetall(key)
            # print(f"get_task_status: {res}")
            return res
        except Exception as e:
            logger.error("get_task_status error")
            logger.error(e)
            raise Exception("get_task_status error")
    # async def set_img_url(self, img_id: str, img_url: str):
    #     """设置图像url"""
    #     key = f"{TASK_IMG_URL_PREFIX}{img_id}"
    #     try:
    #         await self.ensure_connection()
    #         await self.redis_client.set(key, img_url)
    #     except Exception as e:
    #         logger.error("set_img_url error")
    #         logger.error(e)
    #         raise Exception("set_img_url error")
    # async def get_img_url(self, img_id: str):
    #     key = f"{TASK_IMG_URL_PREFIX}{img_id}"
    #     try:
    #         await self.ensure_connection()
    #         return await self.redis_client.get(key)
    #     except Exception as e:
    #         logger.error("get_img_url error")
    #         logger.error(e)
    #         raise Exception("get_img_url error")
    async def add_task_to_queue(self, task_id: str, data: dict, ttl: int = 3600) -> bool:
        """添加任务到队列"""
        try:
            # 保存任务数据
            await self.ensure_connection()
            await self.redis_client.set(
                f"{TASK_DATA_PREFIX}{task_id}", 
                json.dumps(data, default=str),
                ex=ttl
            )
            # 添加到队列
            result = await self.redis_client.rpush(TASK_QUEUE_KEY, task_id)
            return result > 0
        except Exception:
            raise Exception("add_task_to_queue error")

    async def get_next_task(self) -> Optional[tuple[str, dict]]:
        """获取下一个任务"""
        await self.ensure_connection()
        task_id = await self.redis_client.lpop(TASK_QUEUE_KEY)
        if not task_id:
            return None
            
        task_data = await self.redis_client.get(f"{TASK_DATA_PREFIX}{task_id}")
        if task_data:
            return task_id, json.loads(task_data)
        return None

    async def delete_task(self, task_id: str):
        await self.ensure_connection()
        """删除任务相关的所有数据"""
        await self.redis_client.delete(
            f"{TASK_STATUS_PREFIX}{task_id}",
            f"{TASK_DATA_PREFIX}{task_id}"
        )

# 创建全局 Redis 管理器实例
redis_manager = RedisManager()