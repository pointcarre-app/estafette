from _typeshed import Incomplete
from logging import Logger

class Configuration:
    host: str
    temp_folder_path: Incomplete
    api_key: dict[str, str]
    api_key_prefix: Incomplete
    refresh_api_key_hook: Incomplete
    username: str
    password: str
    logger: Logger
    logger_stream_handler: Incomplete
    logger_file_handler: Incomplete
    verify_ssl: bool
    ssl_ca_cert: Incomplete
    cert_file: Incomplete
    key_file: Incomplete
    assert_hostname: Incomplete
    connection_pool_maxsize: Incomplete
    proxy: Incomplete
    safe_chars_for_path_param: str

    def __init__(self) -> None: ...
    
    @classmethod
    def set_default(cls, default) -> None: ...
    
    @property
    def logger_file(self): ...
    
    @logger_file.setter
    def logger_file(self, value) -> None: ...
    
    @property
    def debug(self): ...
    
    @debug.setter
    def debug(self, value) -> None: ...
    
    @property
    def logger_format(self) -> str: ...
    # logger_formatter: Incomplete # NOTE mad: removed from auto gen
    
    @logger_format.setter
    def logger_format(self, value) -> None: ...
    
    def get_api_key_with_prefix(self, identifier): ...
    
    def get_basic_auth_token(self): ...
    
    def auth_settings(self): ...
    
    def to_debug_report(self): ...
