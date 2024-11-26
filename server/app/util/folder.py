from pathlib import Path

class Folder:
    def __init__(self, path: str):
        """
        获取完整路径
        """
        self.__path = Path.joinpath(Path(__file__).parent.absolute().parent.parent, 'static').joinpath(path)
        if not self.__path.exists():
            self.__path.mkdir(parents=True, exist_ok=True)

    def path(self) -> Path:
        return self.__path


