import yaml, os
from ruamel.yaml import YAML
from uuid import uuid4
from asyncio import Semaphore


class ConfigurationYaml:
    def __init__(
        self,
        mapping: int = 2,
        sequence: int = 4,
        offset: int = 2,
        default_fs: bool = False,
        enc: str = "utf-8",
    ) -> None:
        yaml2 = YAML()
        yaml2.indent(mapping=mapping, sequence=sequence, offset=offset)
        yaml2.default_flow_style = default_fs
        yaml2.encoding = enc
        self.yaml_conf = yaml2


class UGUtils:
    def __init__(self, yaml_file: str) -> None:
        self.path = yaml_file
        self.data = self.get_yaml()

    def get_yaml(self) -> dict:
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as file:
                file.write("")

        with open(self.path, encoding="utf-8") as file:
            data = yaml.safe_load(file)

            if not data:
                return {}
            return data


    def update_yaml(self, data: dict):
        yaml_config = ConfigurationYaml().yaml_conf
        with open(self.path, "w", encoding="utf-8") as file:
            data = yaml_config.dump(data, file)

        if data:
            return data
        return {}


class Chanel:
    def __init__(self, data : dict):
        self.id : str = data.get('id')
        self.username : str = data.get('username')
        self.name = data.get('name')
        self.url = data.get('url')
        self.request_join = data.get('request_join', False)
        self.auto_join = data.get('auto_join', False)
        self.user_count = data.get('user_count', 0)

    @property
    def row_data(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'url': self.url,
            'request_join': self.request_join,
            'auto_join': self.auto_join,
            'user_count': self.user_count
        }
    
    def __str__(self):
        return str({
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'url': self.url,
            'request_join': self.request_join,
            'auto_join': self.auto_join,
            'user_count': self.user_count
        })


class DatabseConfig:
    def __init__(self, data : dict) -> None:
        self.user = data.get('user', 'postgres')
        self.pasword = data.get("pasword", '1234')
        self.database = data.get("database", 'database')
        self.port = data.get('port', 5432)
        self.host = data.get('host', 'localhost')

class ParamsManager:
    def __init__(self, config_path : str) -> None:
        self.yaml = UGUtils(config_path)
        self.params_data = self.yaml.get_yaml()
    
        self.config = DatabseConfig(self.params_data.get('database', {}))
        self.TOKEN = self.params_data.get('token')
        self.DATA_CHANEL_ID : int = self.params_data.get('data_chanel_id')
        self.DATA_CHANEL_USERNAME : str = self.params_data.get('data_chanel_username')
        self.DEV_ID : int = self.params_data.get('dev_id')
        self.CONTACT_ADMIN : str = self.params_data.get('contact_admin', 'TemirovDS')
        self.PROTECT_CONTENT : bool = self.params_data.get('protect_content', True)
        self.HELP_CONTENT = self.params_data.get('help_content')

        self.CHANELS : list[Chanel] = [Chanel(chanel) for chanel in self.params_data.get('chanels', [])]
        self.CHANELS_DICT = {chanel.id : chanel for chanel in self.CHANELS}
        self.paramas_sem = Semaphore()
    
    async def update_params(self):
        async with self.paramas_sem:
            self.yaml.update_yaml(self.params_data)

    def update_chanel_dict(self):
        self.CHANELS_DICT = {chanel.id : chanel for chanel in self.CHANELS}