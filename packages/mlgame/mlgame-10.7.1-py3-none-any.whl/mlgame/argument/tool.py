import copy
import json

from mlgame.argument.model import UserNumConfig, GroupAI, AINameEnum
from mlgame.utils.logger import logger


def get_data_from_json_file(file_path) -> dict:
    """
    open json file and return dict data
    """
    with open(file=file_path, mode="rb") as f:
        config_data = json.load(f)
    return config_data


def revise_ai_clients(ai_clients: list[GroupAI], user_num_config: UserNumConfig)->list[GroupAI]:
    ai_clients_result = ai_clients.copy()
    if len(ai_clients) < user_num_config.min:
        logger.warning("提供的ＡＩ數量小於遊戲最小所需ＡＩ數量，系統將會使用最後一個ＡＩ自動補足")
        index =2
        while len(ai_clients_result) < user_num_config.min:

            ai_client = copy.deepcopy(ai_clients[-1])
            ai_client.ai_name=AINameEnum(f"{index}P")
            ai_clients_result.append(ai_client)
            index += 1
    elif len(ai_clients) > user_num_config.max:
        logger.warning("提供的ＡＩ數量高過遊戲容許範圍，系統將會忽略倒數幾個ＡＩ")
        ai_clients_result = ai_clients[:user_num_config.max]
    return ai_clients_result
