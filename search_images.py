from search import StrataSearch


class SearchImages(StrataSearch):
    def __init__(self, url):
        super(SearchImages, self).__init__(url)

    def parse_response(self, data):
        print data
        for item in data['response']['docs']:
            if 'allTitle' not in item:
                print 'The image name is not present'
                continue

            yield item.get('allTitle')
