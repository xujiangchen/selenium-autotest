import os


def get_current_project_path():
    """
    获取当前项目的根目录
    """
    base_path = os.path.split(os.path.dirname((os.path.abspath(__file__))))[0]
    return base_path