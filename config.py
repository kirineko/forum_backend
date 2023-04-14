import configparser
import os

SECRET_KEY = "80b8b60a7fc38000b295c01b958cd176beee89cd0645d0474b25898dfe98864a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

root_folder_path = os.path.dirname(os.path.abspath(__file__))

_config_path = os.path.join(root_folder_path, "config", "server.ini")
_serverConfig = configparser.ConfigParser()
_serverConfig.read(_config_path)

mongo_config = {
    key: {
        "host": _serverConfig.get(f"mongo_{key}", "host"),
        "port": _serverConfig.getint(f"mongo_{key}", "port"),
        "user": _serverConfig.get(f"mongo_{key}", "user") or "",
        "password": _serverConfig.get(f"mongo_{key}", "psw") or "",
        "db_name": _serverConfig.get(f"mongo_{key}", "name"),
    }
    for key in ["forum"]
}
