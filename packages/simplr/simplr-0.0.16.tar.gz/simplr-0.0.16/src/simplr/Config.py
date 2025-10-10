import os
import pickle
import getpass

from .CLI import CLI

class Config:

    USER: str = getpass.getuser()
    CACHE_DIRECTORY: str = f"C:\\Users\\{USER}\\.simplr"
    CACHE_NAME: str = "config.pkl"
    
    def __init__(self):

        cache = os.path.join(Config.CACHE_DIRECTORY, Config.CACHE_NAME)

        self.google_api_key: str = ""
        self.cache_chats: bool = False
        self.platform: str = ""
        self.max_search_depth = 1

        if not os.path.exists(cache):
            self.create_config()
        else:
            with open(cache, "rb") as file:
                self.__dict__.update(pickle.load(file).__dict__)

    def create_config(self):

        cache = os.path.join(Config.CACHE_DIRECTORY, Config.CACHE_NAME)
        self.__dict__.update(CLI.create_config())
        os.makedirs(Config.CACHE_DIRECTORY, exist_ok=True)
        with open(cache, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def _clear_cache():
        cache = os.path.join(Config.CACHE_DIRECTORY, Config.CACHE_NAME)
        if os.path.exists(cache):
            os.remove(cache)  

config = None
def get_config():
    global config
    if config is None:
        config = Config()
    return config
