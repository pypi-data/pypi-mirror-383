import json
from os import path

import orjson
import pydantic
import pytest

from mlgame.argument.tool import revise_ai_clients, get_data_from_json_file
from mlgame.argument.model import UserNumConfig
from mlgame.core.model import GameProgressSchema
from mlgame.view.audio_model import MusicProgressSchema


def test_UserNum():
    try:
        user_num_config = UserNumConfig(min=2, max=1)
        assert False
    except Exception as e:
        assert isinstance(e, pydantic.ValidationError)


@pytest.mark.parametrize(
    "   ai_clients_files        ,min,max,expected_ai_count",
    [
        (['./1p.py', './2p.py'] ,1  ,2  ,2),
        (['./1p.py', './2p.py'] ,1  ,4  ,2),
        (['./1p.py']            ,1  ,2  ,1),
        (['./1p.py']            ,2  ,2  ,2),
        (['./1p.py']            ,4  ,5  ,4),
        (['./1p.py','./2p.py']  ,4  ,5  ,4),
        (['./1p.py','./2p.py']  ,4  ,5  ,4),
        pytest.param(['./1p.py','./2p.py']  ,4  ,5  ,5, marks=pytest.mark.xfail)
    ])
def test_revise_ai_clients(ai_clients_files: list, min: int, max: int, expected_ai_count: int):

    user_num_config = UserNumConfig(min=min, max=max)
    ai_clients = revise_ai_clients(ai_clients_files, user_num_config=user_num_config)
    assert len(ai_clients) == expected_ai_count


def test_open_config_file():
    config_file = path.join(path.dirname(__file__), "test_data", "game_config.json")
    config_data = get_data_from_json_file(config_file)
    assert isinstance(config_data, dict)


def test_dict_contains_key():
    obj = {'key':'value'}

    if 'key' in obj:
        var = obj['key']
    obj = {}
    assert obj.get('key') is None

    music ={'music_id':'musiccc'}
    MusicProgressSchema(**music)

    music = {'type':'music','music_id': 'musiccc'}
    MusicProgressSchema(**music)


def test_orjson_parse_obj():
    data = GameProgressSchema(frame=1)

    assert orjson.dumps(data.model_dump())
    assert json.dumps(data.model_dump())