import os
import sys
import shutil
import uuid
from fastapi import UploadFile, HTTPException

def get_base_dir() -> str:
    """极其关键：获取真实的运行根目录，完美兼容 PyInstaller 与开发环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 EXE 运行，获取 EXE 文件所在的真实物理路径
        return os.path.dirname(sys.executable)
    else:
        # 开发环境下，返回项目根目录 (即 utils 文件夹的上一级)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 统一管理所有核心路径，基于绝对路径
BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
DB_DIR = os.path.join(DATA_DIR, "db")

def ensure_runtime_dirs():
    """确保所有运行时需要的文件夹都存在，如果不存在则立刻自动创建"""
    for d in [DATA_DIR, UPLOAD_DIR, OUTPUT_DIR, DB_DIR]:
        os.makedirs(d, exist_ok=True)

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB

async def save_uploaded_file_fastapi(file: UploadFile) -> str:
    """保存前端上传的文件，支持大文件流式写入，自动处理重名"""
    ensure_runtime_dirs()

    filename = getattr(file, "filename", "temp_file.bin")
    name, ext = os.path.splitext(filename)
    safe_name = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    total_size = 0
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                buffer.close()
                os.remove(file_path)
                raise HTTPException(status_code=413, detail=f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB")
            buffer.write(chunk)

    return file_path

def build_output_path(filename: str) -> str:
    """构建输出文件（如填好的表格）的保存路径"""
    ensure_runtime_dirs()
    return os.path.join(OUTPUT_DIR, filename)

# 如果你的其他代码里还用到了 get_upload_dir 等函数，为了兼容性可以在下面补上：
def get_upload_dir() -> str:
    ensure_runtime_dirs()
    return UPLOAD_DIR