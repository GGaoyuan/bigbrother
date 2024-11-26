from pathlib import Path

class File:
    def __init__(self, foder_path: Path, name: str):
        pass
        # if not all(isinstance(item, str) for item in folder_link):
        #     raise ValueError("列表中的所有元素必须是字符串")
        # path = os.path.join(Path(__file__).parent.absolute().parent.parent, 'static')
        # for folder in folder_link:
        #     path = os.path.join(path, folder)
        # self.__path = path
        # self.__make_dir()