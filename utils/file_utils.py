import os


def get_current_project_path():
    """
    获取当前项目的根目录
    """
    base_path = os.path.split(os.path.dirname((os.path.abspath(__file__))))[0]
    return base_path


def get_subdirectories(folder_path):
    """
    取指定文件夹路径下的所有子目录的完整路径列表
    """
    subdirectories = [f.path for f in os.scandir(folder_path) if f.is_dir()]
    return subdirectories
