class IncorrectJsonException(Exception):
    def __init__(self, status, url, json):
        self.status = status
        self.url = url
        self.json = json

    def __str__(self):
        return 'URL {0} retunred status {1} and ' \
               'incorrect json {2}.'.format(self.url, self.status, self.json)


class IncorrectConfigFileException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "Somethig wrong with config file, please check it. Traceback: {}".format(self.message)