#!/usr/bin/env python

"""A simple example showing to use the Service.job method to retrieve
a search Job by its sid.
"""
import sys
import os
from collections import namedtuple

from sortedcontainers import sorteddict
from time import sleep
from xml.etree import ElementTree

from crane_repo import CraneRepositories
from search_images import SearchImages
from utils.xmltodict import XmlDictConfig
import splunklib.client as client
import datetime
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ImagePullStats = namedtuple('ImagePullStat', ['repository', 'end_date', 'registry', 'value', 'metric_type',
                                              'start_date'])


def execute_splunk_search(**kwargs):
    service = client.connect(**kwargs)
    earliest = '-'+str(kwargs['time_delta'])+kwargs['delta_type']
    print 'getting pull stat of %s' % kwargs['image_name']
    job = service.jobs.create('search index=* host=crane0*.web.prod* \"/v2/'+kwargs['image_name'] +
                              '/manifests\" status = 302 |stats count',
                              exec_mode='blocking', earliest_time=earliest,
                              latest=datetime.time.hour)
    blocking_results = job.results(count=0)
    content = blocking_results.read()

    root = ElementTree.fromstring(content)
    xmldict = XmlDictConfig(root)
    return xmldict['result']['field']['value']['text']


def __get_end_date():
    now = datetime.datetime.utcnow()
    end_date = now.strftime('%Y%m%dT%H:%M:%S.%f')[:-3]
    end_date_tz = end_date + datetime.datetime.now(pytz.timezone("GMT")).strftime('%z')
    return end_date_tz


def __get_image_list(**kwargs):
    if kwargs['crane_host'] is not None:
        crane = CraneRepositories(kwargs['crane_host']+'/crane/repositories/v2')
        return list(crane.get())

    images = SearchImages(kwargs['search_host'] + '/rs/search')
    images.rows = 1000
    return list(images.search('documentKind:ImageRepository'))


def __calculate_start_datetime(delta_type, delta):
    if delta_type == 'd':
        return datetime.datetime.utcnow() - datetime.timedelta(days=delta)
    else:
        return datetime.datetime.utcnow() - datetime.timedelta(hours=delta)


def __get_start_date(delta_type, delta):
    start_date = __calculate_start_datetime(delta_type, delta)
    start_date_str = start_date.strftime('%Y%m%dT%H:%M:%S.%f')[:-3]
    return start_date_str + datetime.datetime.now(pytz.timezone("GMT")).strftime('%z')


def get_stats(**kwargs):
    """
    Retrieves the pull stats of the image list retrieved from search
    :param kwargs: hash containing configuration required to connect to search as well as splunk
    :return: a sorted dictionary that contains among other details the name of image and its
              pull statistics
    """
    stats = {}
    image_list = __get_image_list(**kwargs)
    data = []

    end_date_tz = __get_end_date()

    start_date_tz = __get_start_date(kwargs['delta_type'], kwargs['time_delta'])
    for image in image_list:
        kwargs['image_name'] = image
        if image == 'test/testrep':
            continue
        count = execute_splunk_search(**kwargs)
        print 'pull stat of %(image)s is %(pull)s' % {'image': image,
                                                      'pull': count}
        stat_tuple = ImagePullStats(repository=image, end_date=end_date_tz, registry='registry.access.redhat.com',
                                    value=count, metric_type='pull', start_date=start_date_tz)
        data.append(stat_tuple.__dict__)
        sleep(2)
        stats['data'] = data
    stats['objectType'] = kwargs['save_entity']
    stats['version'] = kwargs['save_entity_version']
    return sorteddict.SortedDict(stats)



