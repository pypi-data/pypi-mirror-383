import os
from typing import List, Union
from uuid import uuid4
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64
import logging as logger
from .http_requests import AsyncHttpClient
urllib3.disable_warnings(InsecureRequestWarning)

import hashlib
from .data.config import EOS_BUCKETID, EOS_APPID, EOS_TOKEN_URL, EOS_URL, EOS_SAVE_DATA_URL, EOS_ONLINE_URL, EOS_SECRET, UPLOAD_TEMP_PATH
from boto3.s3.transfer import TransferConfig
from boto3.session import Session
import base64
import shutil

# 设置日志级别

# 判断是否为空的eos配置
def is_empty_eos_config():
    return EOS_BUCKETID == "" or EOS_APPID == "" or EOS_SECRET == "" or EOS_TOKEN_URL == "" or EOS_URL == "" or EOS_SAVE_DATA_URL == "" or EOS_ONLINE_URL == ""

VERIFY = False
def calculate_md5(file_path: str, block_size: int = 4096) -> str:
    """
    计算指定文件的 MD5 散列值（hex string）。

    :param file_path: 本地文件路径
    :param block_size: 每次读取的字节块大小（默认 4096）
    :return: 文件内容的 MD5 值（长度为 32 的十六进制字符串）
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def get_upload_token():
    url = f"{EOS_TOKEN_URL}"
    original_string = f"{EOS_APPID}:{EOS_SECRET}"
    byte_data = original_string.encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(byte_data).decode("utf-8"),
        "AppId": EOS_APPID
    }
    
    json_data = {
        "bucketId": EOS_BUCKETID
    }

    try:
        # logger.info(f"AsyncHttpClient 实例化完成，verify_ssl=False 是否生效: {http.ssl_context is None}")
        result = requests.post(url, headers=headers, json=json_data, verify=VERIFY)  # verify=False 忽略 HTTPS 证书校验（仅测试用）
        if result.status_code != 200:
            raise Exception(f"get upload token failed, status_code: {result.status_code}, text: {result.text}")
        if result.json()["code"] == 1:
            logger.error(f"图片上传EOS失败")
            raise Exception(f"get upload token failed, 图片上传EOS失败")
        logger.debug(f"get upload token success, result: {result.json()}")
        token = result.json()["data"]
        return token
    except requests.RequestException as e:
        raise Exception(f"HTTP Request failed: {e}")

    except Exception as e:
        raise Exception(f"upload data to eos occur error : {e}")

def save_data(file_path, file_type, obj_name, actual):
    url = EOS_SAVE_DATA_URL
    original_string = f"{EOS_APPID}:{EOS_SECRET}"
    byte_data = original_string.encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(byte_data).decode("utf-8"),
        "AppId": EOS_APPID
    }
    json_data = {
        "bucketId": EOS_BUCKETID,
        "path": obj_name,
        "contentHash": actual,
        "contentSize": os.path.getsize(file_path),
        "contentType": file_type
    }

    try:
        result = requests.post(url, headers=headers, json=json_data, verify=VERIFY) 
        if result.status_code != 200:
            raise Exception(f"save data to eos database failed, status_code: {result.status_code}, text: {result.text}")
        logger.debug(f"save data to eos database success, result: {result}")
        data = result.json()["data"]
        return data
    except requests.RequestException as e:
        raise Exception(f"HTTP Request failed: {e}")
    except Exception as e:
        raise Exception(f"save data to eos database occur error : {e}")
    


def upload_file_to_eos(file_path, access_key, secret_key, token, object_name, bucket, content_type):
#     # -*- coding: utf-8 -*-
#     # Client 初始化
#     # 填写 EOS 账号的认证信息，或者子账号的认证信息
#     # 填写 url。例如：'https://IP:PORT' 或者 'https://eos-wuxi-1.cmecloud.cn'
    url = EOS_URL
    try:
        session = Session(access_key, secret_key, token)
        s3_client = session.client('s3', endpoint_url=url)
        # EOS存储桶和对象键（文件名）  
        bucket_name = bucket
        # 要上传的文件路径  
        
        # actual = calculate_md5(file_path)
        
        # 配置上传行为  
        trans_config = TransferConfig(
            multipart_threshold=5 * 1024 * 1024,  # 超过5MB的文件使用分块上传  
            max_concurrency=10,                  # 最大并发数为10  
            multipart_chunksize=5 * 1024 * 1024,  # 每个分块大小为5MB  
            use_threads=True                     # 使用线程加速上传  
        )
        # file_size = os.path.getsize(file_path)
        # 打开文件并获取文件对象  
        
        with open(file_path, 'rb') as f:
            # 使用高级API上传文件对象
            s3_client.put_object(f, bucket_name, object_name, ExtraArgs={"ContentType": content_type, 'ACL': 'public-read'})
            # s3_client.upload_fileobj(f, bucket_name, object_name, ExtraArgs={"ContentType": content_type, 'ACL': 'public-read'}, Config= trans_config ) #, Callback = lambda x: logger.info(f"upload file to eos size of {x}")
        logger.info(f"{file_path} 上传成功")

    except Exception as e:
        raise Exception(f"upload to eos error occur {e}")
    
def get_content_type(file_extension):
    """
    根据文件后缀获取对应的Content-Type（MIME类型）
    
    参数:
        file_extension: 文件后缀（带不带点都可以，如'.txt'或'txt'）
    
    返回:
        str: 对应的Content-Type，默认返回'application/octet-stream'
    """
    # 统一处理后缀：转为小写，去掉可能的点
    ext = file_extension.lower().lstrip('.')
    
    # MIME类型映射表，可根据需要扩展
    mime_types = {
        # 图片类型
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp',
        'svg': 'image/svg+xml',
        
        # 3D模型类型
        'ply': 'model/x-ply',
        'glb': 'model/gltf-binary',
        'gltf': 'model/gltf+json',
        'obj': 'model/obj',
        'stl': 'model/stl',
        
        # 文本类型
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'text/javascript',
        'csv': 'text/csv',
        'md': 'text/markdown',
        
        # 文档类型
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        
        # 压缩文件
        'zip': 'application/zip',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        'rar': 'application/vnd.rar',
        
        # 其他常见类型
        'json': 'application/json',
        'xml': 'application/xml',
        'mp3': 'audio/mpeg',
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo'
    }
    
    # 查找对应的MIME类型，找不到则返回默认值
    return mime_types.get(ext, 'application/octet-stream')

def get_image_type(urls: Union[str, List[str]]) -> str:
    """
    判断图像类型，通过文件的后缀名进行判断。
    
    :param url: 图像文件的 URL
    :return: 图像类型（如 'png', 'jpeg', 'gif', 'bmp'）或 'unknown'
    """
    # 统一转为列表处理
    if isinstance(urls, str):
        urls = [urls]
        
    for url in urls:
            # 提取文件名及其扩展名
        url_without_query = url.split('?')[0]
        file_name = os.path.basename(url_without_query)
        _, extension = os.path.splitext(file_name)
            # 去掉点号并转换为小写
        extension = extension.lower().lstrip('.')
            # 检查扩展名是否是常见图像类型
        # if extension not in ('png', 'jpeg', 'jpg', 'bmp', 'webp'):
        #     return False # 统一返回 'jpeg'
    return extension

import time
async def download_file(url, save_folder = None, ext = None):
    try:
        http = await AsyncHttpClient.get_instance(verify_ssl=False)
        local_url = url
        if os.path.exists(local_url):
            return (local_url, get_image_type(local_url))
        
        logger.debug(f"download_file: {url}, ext is {ext}")
        if ext:
            file_type = ext
        else:
            file_type = get_image_type(url)
        # if file_type == "unknown":
        #     raise Exception("only support png, jpeg, jpg, bmp, webp")
        if save_folder:
            file_path = f"{save_folder}/{id}.{file_type}"
        else:
            # 放在temp 文件夹下
            id = uuid4()
            file_path = f"{UPLOAD_TEMP_PATH}/{id}.{file_type}"
        
        response = await http.download_file(url, file_path)
        logger.debug(f"download_file: {file_path}")
        return (response, file_type)
    except Exception as e:
        logger.error(f"Error occurred in download_file: {e}")
        raise Exception(f"Error occurred in download_file: {e}")
    
def upload_file(file_path, callback: callable = None, ext: str = None):

    # assert is_empty_eos_config() == True, "请检查环境变量EOS_XXX 是否配置正确"

    Max_retry = 3  # 最大重试次数
    retry_delay = 1  # 初始重试延迟（秒）
    
    for attempt in range(Max_retry):
        try:
            if file_path.startswith("http"):
                # 下载文件
                file_path, _ = download_file(file_path, ext=ext)
            
            # 获取文件md5
            file_id = uuid4()
            actual = calculate_md5(file_path)
            logger.debug(f"md5的值是：{actual}")
            
            # 获取文件类型和文件名称
            file_name = os.path.basename(file_path)
            _, file_ext = os.path.splitext(file_name)
            eos_file_name = f"{file_id}{file_ext}"
            file_type = get_content_type(file_ext)
            
            # 获取凭证
            token_info = get_upload_token()
            obj_name = f'{token_info["RootDir"]}/{EOS_APPID}/{actual}/{eos_file_name}'
            
            # 上传文件
            upload_file_to_eos(
                file_path, 
                token_info['AccessKeyId'], 
                token_info['SecretAccessKey'], 
                token_info["SessionToken"], 
                obj_name, 
                token_info["Bucket"], 
                file_type
            )
            
            # 上传数据库
            save_data(file_path, file_type, eos_file_name, actual)
            
            dir = f"{EOS_ONLINE_URL}{eos_file_name}"
            logger.debug(f"dir is {dir}")
            return dir 
        
        except Exception as e:
            # 如果是最后一次尝试，则抛出异常
            if attempt == Max_retry - 1:
                raise Exception(f"达到最大重试次数，文件上传失败: {str(e)}")
            # 记录重试信息
            logger.warning(f"第 {attempt + 1} 次上传失败: {str(e)}，将在 {retry_delay} 秒后重试")
            
            # 等待一段时间后重试，指数退避策略
            time.sleep(retry_delay)
            retry_delay *= 2  # 每次重试延迟翻倍，减少服务器压力

    # 理论上不会到达这里，因为循环内要么返回要么抛出异常
    raise Exception("未知错误，文件上传失败")
    

def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            # 递归删除文件夹及其内容
            # shutil.rmtree(folder_path)
            os.remove(file_path)
            logger.debug(f"文件 '{file_path}' 已成功删除")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    else:
        logger.debug(f"文件夹 '{file_path}' 不存在")
        return False
def delete_folder(folder_path):
    # 判断是文件么
    # 判断该路径是否为目录（实际脚本通常是文件，所以此判断可能返回 False）
    if not os.path.isdir(folder_path):
        # 如果是目录，直接使用该路径
        folder_path = os.path.dirname(folder_path)
    
    # 检查文件夹是否存在
    if os.path.exists(folder_path):
        try:
            # 递归删除文件夹及其内容
            shutil.rmtree(folder_path)
            logger.debug(f"文件夹 '{folder_path}' 已成功删除")
            return True
        except Exception as e:
            logger.error(f"删除文件夹失败: {e}")
            return False
    else:
        logger.error(f"文件夹 '{folder_path}' 不存在")
        return False
    
