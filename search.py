__author__ = 'A.P. Rajshekhar'
import requests


class StrataSearch(object):
    def __init__(self, search_url):
        self.url = search_url

    def search(self, query):
        """
        Executes a search based on the query and returns generator containing the name of
        the ISV
        :param query: basestring containing the query to be executed for ISV images
        :return: generator
        """
        param = {
            'q': query,
            'rows': self._rows
            }
        headers = {'Accept': 'application/vnd.redhat.solr+json'}
        print self.url
        response = requests.get(self.url, params=param, headers=headers, verify=False)

        print response.url
        data = response.json()
        # print data

        result = self.parse_response(data)
        return result

    def parse_response(self, data):
        for item in data['response']['docs']:
            if 'c_pull_command' not in item:
                print "%s does not have pull command" % item.get('allTitle')
                continue

            for value in item.get('c_pull_command'):
                    name = value.replace('docker pull', '', 1).strip()
                    yield name

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value

