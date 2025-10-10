import os
import getpass
import pickle

class Cache:

    USER: str = getpass.getuser()
    CACHE_DIRECTORY: str = f"C:\\Users\\{USER}\\.simplr"
    CACHE_NAME: str = "cache.pkl"

    @staticmethod
    def cache(obj, path: str | None = None):

        cache = os.path.join(Cache.CACHE_DIRECTORY, Cache.CACHE_NAME)

        current_cache = {}

        if not path:
            path = os.getcwd()

        if (os.path.exists(cache)):
            with open(cache, "rb") as file:
                current_cache = pickle.load(file)

        obj["messages"] = obj["messages"][:-1]
        current_cache[path] = obj

        with open(cache, "wb") as file:
            pickle.dump(current_cache, file)

    @staticmethod
    def get():

        cache = os.path.join(Cache.CACHE_DIRECTORY, Cache.CACHE_NAME)

        if (os.path.exists(cache)):
            with open(cache, "rb") as file:
                loaded = pickle.load(file).get(os.getcwd())
                return loaded["messages"][-10:] if loaded else []
        
        return []

    @staticmethod
    def _clear_cache():
        os.remove(os.path.join(Cache.CACHE_DIRECTORY, Cache.CACHE_NAME))
