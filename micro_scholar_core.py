"""
Micro-Scholar Core API Definition
"""
import abc

class DataProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def fetch_new_content(self):
        """从远程源（飞书/API）获取新内容并写入本地库"""
        pass

    @abc.abstractmethod
    def get_random_item(self):
        """从本地库随机抽取一条展示"""
        pass

class FeishuManager(DataProvider):
    """处理飞书文档/多维表格的同步逻辑"""
    def __init__(self, app_id: str, app_secret: str):
        self.client = None # Lark SDK Client
    
    def sync_folder(self, folder_token: str):
        """遍历文件夹，解析所有 Docsx 文档的 Text Block"""
        pass

class ProcessMonitor:
    """监听系统进程，判断是否进入等待/完成状态"""
    def is_waiting_for_build(self, process_names=["make", "gcc", "python"]) -> bool:
        pass

class ScholarUI(abc.ABC):
    """UI 展示基类"""
    @abc.abstractmethod
    def show_toast(self, title: str, content: str, duration=5):
        pass