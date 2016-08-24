#!/usr/bin/env python

"""A simple example showing to use the Service.job method to retrieve
a search Job by its sid.
"""

import sys
import os
import datetime
from collections import namedtuple

import yaml
from sortedcontainers import sorteddict
from time import sleep
from xml.etree import ElementTree

from search_images import SearchImages
from utils.xmltodict import XmlDictConfig
import splunklib.client as client
from utils import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ImagePullStats = namedtuple('ImagePullStat', ['image_name', 'pulls', 'time'])

CONFIG_FILE_PATH = '/etc/config.yaml'
CONFIG_ENV_NAME = 'CONFIG_FILE_PATH'


def execute_splunk_search(**kwargs):
    service = client.connect(**kwargs)
    # kept for future reference
    # Execute a simple search, and store the sid
    # sid = service.search("search host=crane0*.web.prod* sourcetype=access_combined  \"/v1/repositories/openshift3/logging-kibana/images\" | stats count ", earliest="08/15/2016:01:00:00", latest="08/15/2016:23:59:30").sid
    #
    # # Now, we can get the `Job`
    # job = service.job(sid)
    #
    # # Wait for the job to complete
    # while not job.is_done():
    #     print 'waiting for search to be done'
    # print job["resultCount"]
    # rr = results.ResultsReader(io.BufferedReader(job.results()))
    # for result in rr:
    #     if isinstance(result, dict):
    #         # Normal events are returned as dicts
    #         print result

    print 'getting pull stat of %s' % kwargs['image_name']
    job = service.jobs.create('search index=* host=crane0*.web.prod* \"/v1/repositories/'+kwargs['image_name'] +
                              '/images\" status = 200 |stats count',
                              exec_mode='blocking', earliest_time='-1h', latest=datetime.time.hour)
    blocking_results = job.results(count=0)
    content = blocking_results.read()
    # print content
    root = ElementTree.fromstring(content)
    xmldict = XmlDictConfig(root)
    return xmldict['result']['field']['value']['text']


def run(argv):
    config_path = os.environ.get(CONFIG_ENV_NAME) or CONFIG_FILE_PATH
    configuration = None
    try:
        configuration = yaml.safe_load(open(config_path))
    except Exception:
        print 'Could not load configuration.'
    opts = None
    args = {}
    if configuration is None:
        opts = parse(argv, {}, ".splunkrc")
    else:
        args = {
            'host': configuration['host'],
            'username': configuration['username'],
            'password': configuration['password']
            }

    if opts is not None:
        return get_stats(**opts.kwargs)
    return get_stats(args)


def get_stats(**kwargs):
    stats = {}
    images = SearchImages('<host>/rs/search')
    images.rows = 1000
    image_list = list(images.search('documentKind:ImageRepository'))
    for image in image_list:
        kwargs['image_name'] = image
        count = execute_splunk_search(**kwargs)
        print 'pull stat of %(image)s is %(pull)s' % {'image': image,
                                                      'pull': count}
        stat_tuple = ImagePullStats(image, count, datetime.datetime.now().strftime('%H'))
        stats[image] = stat_tuple
        sleep(2)
    return sorteddict.SortedDict(stats)

if __name__ == "__main__":
    # main(sys.argv[1:])
    stats = run(sys.argv[1:])
    print 'stats %s' % stats

