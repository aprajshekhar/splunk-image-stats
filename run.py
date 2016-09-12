import json
import os

import datetime

import sys
import yaml

from oneshot import get_stats


CONFIG_FILE_PATH = '/etc/config.yaml'
CONFIG_ENV_NAME = 'CONFIG_FILE_PATH'


def run():
    config_path = os.environ.get(CONFIG_ENV_NAME) or CONFIG_FILE_PATH
    print os.environ
    configuration = None
    try:
        configuration = yaml.safe_load(open(config_path))
    except Exception:
        print 'Could not load configuration.'
        sys.exit(-1)
    args = {
        'host': configuration['host'] or 'splunk.corp.redhat.com',
        'username': configuration['username'],
        'password': configuration['password'],
        'search_host': configuration['search_host'],
        'search_type': configuration['search_type'] or 'documentKind:ImageRepository',
        'from_time': configuration['start_time'] or '-1h',
        'end_time': configuration['end_time'] or datetime.time.hour
        }

    return get_stats(**args)

if __name__ == "__main__":
    # main(sys.argv[1:])
    stats = run()
    stat_json = json.dumps(stats, indent=4)
    print stat_json