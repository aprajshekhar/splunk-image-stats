import requests
import json


class CraneRepositories(object):
    def __init__(self, search_url):
        self.url = search_url

    def get(self):
        """
        Executes a search based on the query and returns generator containing the name of
        the ISV
        :param query: basestring containing the query to be executed for ISV images
        :return: generator
        """

        headers = {'Accept': 'application/json'}
        print self.url
        response = requests.get(self.url, headers=headers, verify=False)

        print response.url
        data = response.json()
        return data.keys()

if __name__ == '__main__':
    c = CraneRepositories('https://registry.access.redhat.com/crane/repositories/v2')
    print len(list(c.get()))
