
from pydantic import BaseModel
from typing import Literal, Optional, List, Any, Union
from typing import get_origin, get_args
from typing import Type
from pydantic_core import PydanticUndefined
import annotated_types


def is_literal_or_optional(type_hint: Type) -> str:
    """
    判断类型是否是 Literal 或 Optional 类型，返回类型的名称。
    """
    origin = get_origin(type_hint)  # 获取类型的原始类型
    args = get_args(type_hint)      # 获取类型的参数
    # print(f"{type_hint} : {origin} : {args}")
    # 检查是否是 Optional
    if origin is Union and len(args) == 2 and args[1] is type(None):
        return args[0].__name__
    # Optional[str]

    if origin is Union and len(args) == 1:
        return type(args[0]).__name__
    # 检查是否是 Literal
    if origin is Literal:
        return type(args[0]).__name__
    if origin is list:
        return f"{origin.__name__}[{args[0].__name__}]"
    return type_hint.__name__

def generate_metadata(model_class: BaseModel) -> List[dict]:
    metadata = []
    # 遍历模型的字段
    annotations = {**model_class.__annotations__}
    for field_name, field in annotations.items():
        if field_name == "model":
            continue
        field_info = model_class.model_fields[field_name]
        # print("****************************")
        field_type = is_literal_or_optional(field_info.annotation)
        # 准备字段元数据
        # print(f"field_name : {field_name}: field_info.annotation : {field_info.annotation}, field_type: {field_type}")
        # if field_info.annotation in (Literal, Union):
        #     print(type(field_type.__args__[0]).__name__) 
        field_metadata = {
            "key": field_name,
            "label": field_info.title,  # 使用 'label' 字段，默认使用字段名
            "type": field_type,
            "default": field_info.default if field_info.default is not PydanticUndefined else (0 if field_type == "int" else ""),
            "placeholder": field_info.description,
            "component": field_info.json_schema_extra.get("type", "input") if field_info.json_schema_extra else "input",
            "value": field_info.json_schema_extra.get("value", "") if field_info.json_schema_extra else "",
            "required": field_info.is_required(),
        }

        constraints = {}
        for item in field_info.metadata:
            if isinstance(item, annotated_types.Ge):
                constraints['min'] = field_info.metadata[0].ge
            elif isinstance(item, annotated_types.Le):
                constraints['max'] = field_info.metadata[1].le

        limit = {}
        if "list" in field_metadata["type"]:
            field_metadata["max_length"] = field_info.json_schema_extra.get("max_length", 1) if field_info.json_schema_extra else 0
        field_metadata["show"] = field_info.json_schema_extra.get("show", True) if field_info.json_schema_extra else False
        
        if constraints:
            field_metadata.update(constraints)

        metadata.append(field_metadata)

    return metadata


import os
import logging
from zipfile import ZipFile
from .upload_sync import upload_file as upload_file_sync
from .upload import delete_file
async def zip_folder_files(
    source_dir,          # 待压缩的目标文件夹路径
    prompt_id,           # 用于生成压缩包名称的标识（如您原代码中的prompt_id）
    recursive=True,      # 是否递归压缩子目录下的文件（默认True）
    keep_relative_path=True  # 压缩包内是否保留文件的相对路径（默认True，解压后保持目录结构）
):
    """
    压缩指定文件夹下的所有文件（可配置是否包含子目录），并返回上传后的路径
    
    Args:
        source_dir (str): 要压缩的文件夹绝对路径或相对路径
        prompt_id (str): 压缩包名称前缀（最终生成 "prompt_id.zip"）
        recursive (bool): 是否递归处理子目录中的文件，True=包含子目录，False=仅当前目录
        keep_relative_path (bool): 压缩包内文件是否保留相对路径
            - True：如 "source_dir/sub1/file1.png" 会存为 "sub1/file1.png"
            - False：所有文件直接存放在压缩包根目录（可能覆盖同名文件）
    
    Returns:
        str: 上传到eos后的文件路径
    
    Raises:
        NotADirectoryError: 当source_dir不是有效文件夹时抛出
    """
    # 1. 校验目标文件夹是否存在且为有效目录
    if not os.path.exists(source_dir):
        raise NotADirectoryError(f"目标文件夹不存在：{source_dir}")
    if not os.path.isdir(source_dir):
        raise NotADirectoryError(f"不是有效文件夹：{source_dir}")
    
    # 2. 生成压缩包路径（默认与待压缩文件夹同目录，名称为 "prompt_id.zip"）
    # 若需自定义压缩包存放目录，可修改第一个参数（如os.path.join("/tmp", f"{prompt_id}.zip")）
    zip_path = os.path.join("/tmp", f"{prompt_id}.zip")
    
    # 3. 遍历文件夹下所有文件，添加到压缩包
    with ZipFile(zip_path, 'w') as zipf:
        # 遍历目录：os.walk返回 (当前目录, 子目录列表, 文件列表)
        for root, _, files in os.walk(source_dir):
            # 若不递归，仅处理顶层目录（跳过子目录）
            if not recursive and root != source_dir:
                continue
            
            # 遍历当前目录下的所有文件
            for filename in files:
                # 获取文件的绝对路径
                file_abs_path = os.path.join(root, filename)
                
                # 计算压缩包内的文件名（arcname）
                if keep_relative_path:
                    # 保留相对路径（相对于source_dir），解压后保持目录结构
                    arcname = os.path.relpath(file_abs_path, source_dir)
                else:
                    # 仅保留文件名，所有文件放在压缩包根目录
                    arcname = filename
                
                # 将文件添加到压缩包
                zipf.write(file_abs_path, arcname=arcname)
                logging.debug(f"已添加文件到压缩包：{file_abs_path} -> {arcname}")
    
    logging.info(f"压缩包生成完成：{zip_path}")
    
    # 4. 上传到eos（复用您原有的upload_file函数）
    try:
        uploaded_file_path = await upload_file_sync(zip_path)
        logging.debug(f"压缩包已上传至：{uploaded_file_path}")
    except Exception as e:
        logging.error(f"压缩包上传失败：{str(e)}")
        raise  # 抛出异常，让调用方处理
    
    # 5. 删除本地压缩包（复用您原有的delete_file函数）
    try:
        delete_file(zip_path)
        logging.debug(f"本地压缩包已删除：{zip_path}")
    except Exception as e:
        logging.warning(f"删除本地压缩包失败：{str(e)}")  # 上传成功但删除失败，不中断流程
    
    return uploaded_file_path