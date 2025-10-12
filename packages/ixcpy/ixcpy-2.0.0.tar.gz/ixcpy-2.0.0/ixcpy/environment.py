import os
import threading
from dotenv import load_dotenv


class Environment:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                load_dotenv(override=True)
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with self._lock:
            if not hasattr(self, '_initialized'):
                self._load_env_vars()
                self._initialized = True

    def _load_env_vars(self):
        self._domain = os.getenv("IXC_SERVER_DOMAIN")
        self._token = os.getenv("IXC_ACCESS_TOKEN")

    def domain(self) -> str:
        if not self._domain:
            raise EnvironmentError("A variável de ambiente 'IXC_SERVER_DOMAIN' não foi definida")
        return self._domain

    def token(self) -> str:
        if not self._token:
            raise EnvironmentError("A variável de ambiente 'IXC_ACCESS_TOKEN' não foi definida")
        return self._token