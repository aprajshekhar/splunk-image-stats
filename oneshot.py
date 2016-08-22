#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A simple example showing to use the Service.job method to retrieve
a search Job by its sid.
"""

import sys
import os
import datetime
from xml.etree import ElementTree

from utils.xmltodict import XmlDictConfig

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import splunklib.client as client
import splunklib.results as results
import io

try:
    from utils import *
except ImportError:
    raise Exception("Add the SDK repository to your PYTHONPATH to run the examples "
                    "(e.g., export PYTHONPATH=~/splunk-sdk-python.")


def main(argv):
    opts = parse(argv, {}, ".splunkrc")
    service = client.connect(**opts.kwargs)

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

    print 'getting pull stat of %s' % argv[0]
    job = service.jobs.create('search index=* host=crane0*.web.prod* \"/v1/repositories/'+argv[0] +
                              '/images\" status = 200 |stats count',
                              exec_mode='blocking', earliest_time='-1h', latest=datetime.time.hour)
    blocking_results = job.results(count=0)
    content = blocking_results.read()
    # print content
    root = ElementTree.fromstring(content)
    xmldict = XmlDictConfig(root)
    print 'pull stat of %(image)s is %(pull)s' % {'image': argv[0], 'pull': xmldict['result']['field']['value']['text']}
    # print xmldict['result']['field']['value']['text']

if __name__ == "__main__":
    main(sys.argv[1:])

