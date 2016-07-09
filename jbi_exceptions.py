class IncorrectJsonException(Exception):
    def __init__(self, status, url, json):
        self.status = status
        self.url = url
        self.json = json

    def __str__(self):
        return 'URL {0} retunred status {1} and ' \
               'incorrect json {2}.'.format(self.url, self.status, self.json)
