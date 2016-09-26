import json
import os

import datetime

import sys
import yaml

from oneshot import get_stats
from save import save_data

CONFIG_FILE_PATH = '/etc/image-pull-stats/config.yaml'
CONFIG_ENV_NAME = 'CONFIG_FILE_PATH'


def save(configuration, pull_data):
    response = save_data(url=configuration['save_url'], data_json=json.dumps(pull_data, indent=4),
                         cert_path=configuration['cert_path'], cert_passphrase=configuration['passphrase'],
                         save_entity=configuration['save_entity_name'],
                         version=configuration['save_entity_version']
                         )
    return json.loads(response)


def run():
    config_path = os.environ.get(CONFIG_ENV_NAME) or CONFIG_FILE_PATH
    print os.environ
    configuration = {}
    try:
        configuration = yaml.safe_load(open(config_path))
    except Exception:
        print 'Could not load configuration.'
        sys.exit(-1)
    args = {
        'host': configuration['host'],
        'username': configuration['username'],
        'password': configuration['password'],
        'crane_host': configuration['crane_host'],
        'search_host': configuration['search_host'],
        'search_type': configuration['search_type'] or 'documentKind:ImageRepository',
        'time_delta': configuration['time_delta'] or '-2',
        'delta_type': configuration['delta_type'] or 'h',
        'save_entity': configuration['save_entity_name'],
        'save_entity_version': configuration['save_entity_version']
        }

    stats = get_stats(**args)
    resp_data = save(configuration, stats)
    if not resp_data['status'] == "COMPLETE":
        print "Error occurred while populating lightblue entity: %s" % resp_data
        sys.exit(-1)
    return resp_data

if __name__ == "__main__":
    response_data = run()
    print "Pull statistics has been  successfully pushed to lightblue:"
    print response_data