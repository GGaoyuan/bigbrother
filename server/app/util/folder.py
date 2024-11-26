from pathlib import Path

class Folder:
    def __init__(self, folder_link: list[str]):
        """
        获取完整路径
        """
        if not all(isinstance(item, str) for item in folder_link):
            raise ValueError("列表中的所有元素必须是字符串")
        path = Path.joinpath(Path(__file__).parent.absolute().parent.parent, 'static')
        for folder in folder_link:
            path = Path.joinpath(path, folder)
        self.__path = path
        self.__make_dir()

    def __make_dir(self):
        """
        创建文件夹
        """
        path = Path(self.__path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f'{self.__path} already exists')

    def path(self) -> str:
        return self.__path


