
import asyncio
import numpy as np
from PIL import Image
import os
import logging as logger

# renderer = pyrender.OffscreenRenderer(512, 512)
def generate_mesh_thumbnail(
    glb_path, 
    output_path=None, 
    width=512, 
    height=512,
    camera_angle=90,  # 相机倾斜角度（度，可微调俯视/仰视）
    zoom_factor=2   # 缩放系数，控制相机距离
):
    # 覆盖所有可能的环境变量，确保生效
    # os.environ["MESA_GL_VERSION_OVERRIDE"] = "3.3"  # 强制 OpenGL 3.3 版本（兼容性最佳）
    # os.environ["MESA_GLSL_VERSION_OVERRIDE"] = "330"  # 强制 GLSL 330 版本

    import os
    os.environ["PYOPENGL_PLATFORM"] = "egl"  # 禁用 X11，用纯软件渲染
    # os.environ["MESA_GL_VERSION_OVERRIDE"] = "3.3"  # 兼容 pyglet 着色器
    # os.environ["MESA_GLSL_VERSION_OVERRIDE"] = "330"
    # os.environ["EGL_DISABLE"] = "1"  # 禁用 EGL 后端

    # 关键2：确认环境变量生效（日志验证）
    logger.info(f"进程 {os.getpid()} 环境变量：PYOPENGL_PLATFORM={os.environ.get('PYOPENGL_PLATFORM')}")

    # 导入依赖（必须在环境变量设置后）
    import trimesh
    import pyrender
    import numpy as np
    from PIL import Image
    """
    生成GLB文件的缩略图，优化为正面视角
    """
    if not os.path.exists(glb_path):
        logger.info(f"错误: 文件 '{glb_path}' 不存在")
        raise Exception("model_not_found")
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(width, height))
    display.start()
    # os.environ["DISPLAY"] = display.env()["DISPLAY"] 
    print(f"子进程 {os.getpid()} 虚拟显示启动：{os.environ['DISPLAY']}")

    # 处理输出路径
    if output_path is None:
        base_name = os.path.splitext(glb_path)[0]
        output_path = f"{base_name}.png"
    
    # 检查文件是否存在
    if not os.path.exists(glb_path):
        logger.error(f"文件不存在: {glb_path}")
        raise Exception("model_not_found")
    
    # 加载GLB模型
    logger.info(f"加载模型: {glb_path}")
    mesh = trimesh.load(glb_path)
    
    # 验证模型内容
    if isinstance(mesh, trimesh.Scene):
        geometries = list(mesh.geometry.values()) 
        if not geometries:
            logger.error("模型不包含任何几何体")
            raise Exception("模型不包含任何几何体")
        bounding_box = mesh.bounding_box
        centroid = bounding_box.centroid
    else:
        if not mesh.vertices.any():
            logger.error("模型不包含顶点数据")
            raise Exception("模型不包含顶点数据")
        bounding_box = mesh.bounding_box
        centroid = mesh.centroid
    
    # 计算模型尺寸
    extents = bounding_box.extents
    max_extent = np.max(extents)
    model_radius = max_extent / 2
    logger.info(f"模型尺寸: 最大范围 {max_extent:.2f}, 半径 {model_radius:.2f}")
    
    # 创建渲染场景，白色背景
    scene = pyrender.Scene(ambient_light=[0.3, 0.3, 0.3], bg_color=[1.0, 1.0, 1.0])
    
    # 添加模型到场景
    if isinstance(mesh, trimesh.Scene):
        for name, m in mesh.geometry.items():
            render_mesh = pyrender.Mesh.from_trimesh(m)
            scene.add(render_mesh, name=name)
    else:
        render_mesh = pyrender.Mesh.from_trimesh(mesh)
        scene.add(render_mesh)
    
    # 计算相机位置和姿态（正面视角）
    camera_distance = model_radius * zoom_factor * 2
    angle_rad = np.radians(camera_angle)

    # 让相机位于模型正前方（这里假设模型正面朝向Z轴负方向，可根据实际调整）
    # 若模型正面是Z轴正方向，camera_z 改为 camera_distance 即可
    camera_x = 0  # 沿X轴无偏移，正前方观察
    camera_y = 0.5  # 沿Y轴无偏移，正前方观察
    camera_z = camera_distance  # 相机在Z轴负方向，看向模型中心（Z轴正方向为模型正面）

    camera_position = np.array([camera_x, camera_y, camera_z]) + centroid
    logger.info(f"相机位置: {camera_position}")

    # 确保相机看向模型中心（视线方向指向模型中心）
    view_dir = centroid - camera_position
    view_dir = view_dir / np.linalg.norm(view_dir)

    # 创建相机
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 4.0, aspectRatio=width/height)

    # 计算相机姿态矩阵
    up = np.array([0, 1, 0])  # Y轴向上，符合常规视角
    right = np.cross(view_dir, up)
    right = right / np.linalg.norm(right)
    new_up = np.cross(right, view_dir)

    camera_pose = np.eye(4)
    camera_pose[:3, 0] = right
    camera_pose[:3, 1] = new_up
    camera_pose[:3, 2] = -view_dir
    camera_pose[:3, 3] = camera_position
    scene.add(camera, pose=camera_pose)

    # 添加多个光源确保模型可见
    # 主光源 - 相机侧前方
    light1 = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=3.0)
    light1_pose = np.eye(4)
    light1_pose[:3, 3] = camera_position + np.array([camera_distance*0.2, camera_distance*0.2, 0])
    scene.add(light1, pose=light1_pose)

    # 辅助光源 - 模型另一侧
    light2 = pyrender.DirectionalLight(color=[0.8, 0.8, 0.8], intensity=2.0)
    light2_pose = np.eye(4)
    light2_pose[:3, 3] = centroid + np.array([camera_distance*0.2, camera_distance*0.2, 0])
    scene.add(light2, pose=light2_pose)

    # 顶部光源
    light3 = pyrender.PointLight(color=[1.0, 1.0, 0.9], intensity=2.0)
    light3_pose = np.eye(4)
    light3_pose[:3, 3] = centroid + np.array([0, 0, max_extent * 1.5])
    scene.add(light3, pose=light3_pose)
    
    # 选择渲染后端
    try:
        logger.info("使用默认渲染后端")
        r = pyrender.OffscreenRenderer(width, height)
        logger.info(f"进程 {os.getpid()} OSMesa 渲染器初始化成功")
    except Exception as e:
        import traceback
        logger.info(traceback.format_exc())
        logger.warning(f"渲染后端初始化失败: {e}, 尝试备用方案")
        r = pyrender.OffscreenRenderer(width, height)
    
    # 渲染
    logger.info("开始渲染...")
    color, depth = r.render(scene)
    
    # 检查渲染结果
    if np.max(color) < 0.1:  # 几乎全黑
        logger.warning("渲染结果可能过暗，尝试增强光照后重新渲染")
        scene.ambient_light = [0.8, 0.8, 0.8]
        color, depth = r.render(scene)
    
    # ============= 新增：处理透明背景 =============
    # 将颜色数组转换为 PIL Image（带 Alpha 通道）
    # 1. 先转换为 RGBA 模式
    img = Image.fromarray(color.astype(np.uint8)).convert("RGBA")
    data = img.getdata()
    
    # 2. 定义背景色（白色：[255, 255, 255]）
    bg_color = (255, 255, 255, 255)
    new_data = []
    for item in data:
        # 如果像素接近背景色，设置为透明
        if abs(item[0]-bg_color[0]) < 10 and abs(item[1]-bg_color[1]) < 10 and abs(item[2]-bg_color[2]) < 10:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)  # 保留模型像素
    
    # 3. 更新图像数据
    img.putdata(new_data)
    # ============= 透明背景处理结束 =============
    
    # 保存为 PNG（支持透明）
    img.save(output_path, "PNG")
    logger.info(f"透明背景缩略图已保存: {output_path}")
    
    # 清理
    r.delete()
    display.stop()
    logger.info(f"缩略图已生成: {output_path}")
    return output_path

from concurrent.futures import ProcessPoolExecutor
import uuid
from functools import partial

# 全局进程池（复用进程，提高效率）
MAX_WORKERS = os.cpu_count() or 4
_executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)

async def submit_gen_thumbnail(
    glb_path, 
    output_path=None, 
    width=512, 
    height=512,
    camera_angle=90,
    zoom_factor=2,
    loop=None
):
    """
    异步生成单个GLB文件的缩略图
    直接通过协程任务调度，无需单独的队列
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    
    # 确认进程池已初始化
    if _executor is None:
        raise Exception("进程池未初始化！请先调用init_executor()")
    
    # 将同步函数包装为可在进程池执行的任务
    func = partial(
        generate_glb_thumbnail,
        glb_path, output_path, width, height, camera_angle, zoom_factor
    )
    
    # 提交到进程池执行并等待结果
    result = await loop.run_in_executor(_executor, func)
    return result

async def run():
    obj = "/home/migu/cdm/project/Aigc/layout_gen/Materials/3DLayoutGen_20241124/static/scene0d381049-edfa-45c6-bd84-54337c126bc7/complete/MasterBedroom-18517_142_011.ply"
    task1 = asyncio.create_task(submit_gen_thumbnail(obj, "static/scene0d381049-edfa-45c6-bd84-54337c126bc7/complete/MasterBedroom-18517_142_011.png"))
    obj = "/home/migu/cdm/project/Aigc/layout_gen/Materials/3DLayoutGen_20241124/static/scenef373dc5c-4b47-4242-a75d-6daea09cfa9b/complete/MasterBedroom-32488_113_004.ply"
    task2 = asyncio.create_task(submit_gen_thumbnail(obj, "static/scenef373dc5c-4b47-4242-a75d-6daea09cfa9b/complete/MasterBedroom-32488_113_004.png"))
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    # Start Xvfb for headless rendering
    asyncio.run(run())

