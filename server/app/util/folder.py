from pathlib import Path
import os

class Folder:
    def __init__(self, folder_link: list[str]):
        """
        获取完整路径
        """
        if not all(isinstance(item, str) for item in folder_link):
            raise ValueError("列表中的所有元素必须是字符串")
        path = Path.joinpath(Path(__file__).parent.absolute().parent.parent, 'static')
        for folder in folder_link:
            path = os.path.join(path, folder)
        self.__path = path
        self.__make_dir()

    def __make_dir(self):
        """
        创建文件夹
        """
        if len(self.__path) == 0:
            raise ValueError(f'path is none')
        if not os.path.exists(self.__path):
            os.makedirs(self.__path)
        else:
            print(f'{self.__path} already exists')

    def file_exist(self, file_name: str) -> bool:
        """
        文件夹下的文件是否存在
        :param file_name:
        :return:
        """
        file_path = os.path.join(self.__path, file_name)
        if not os.path.exists(file_path):
            return True
        else:
            return False

    def path(self) -> str:
        return self.__path


