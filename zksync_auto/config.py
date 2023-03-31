import os
import logging

from python_json_config import ConfigBuilder
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
CODE_HOME = os.path.abspath(os.path.dirname(__file__) + '/..')
ONEINCH_PACKAGE = os.path.abspath(os.path.dirname(__file__) + '/oneinch/package')
TMP_FOLDER = '/tmp'
TMP_ZKSYNC = '/tmp/zksync'
os.makedirs(TMP_ZKSYNC, exist_ok=True)

ACC_PATH = os.environ.get('ACC_PATH')
try:
    ACC_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.environ.get('ACC_PATH'))
except Exception as e:
    print(e)


def get_config():
    # create config parser
    _builder = ConfigBuilder()

    # parse config
    config_file_path = os.environ.get('CONFIG_FILE_PATH')
    if not config_file_path:
        raise Exception(f'Invalid config file path [{config_file_path}]')

    if not os.path.exists(config_file_path):
        # append to project home path
        config_file_path = os.path.join(os.path.dirname(__file__), os.pardir, config_file_path)

    if not os.path.exists(config_file_path):
        raise Exception(f'Invalid config file path [{config_file_path}]')

    _config = _builder.parse_config(config_file_path)

    return _config


# Use this variable for global project
config = get_config()
