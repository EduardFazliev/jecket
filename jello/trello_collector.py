from trello import TrelloApi

from config import apikey, token


class TrelloCollector(object):
    def __init__(self):
        self.trello = TrelloApi(apikey=apikey)
        self.trello.set_token(token)

    def get_board_lists(self, board_id):
        full_info = self.trello.boards.get_list(board_id)
        short_info = [(lst['name'], lst['id']) for lst in full_info]
        return short_info

    def get_lists_cards(self, list_id):
        cards = self.trello.lists.get_card(list_id=list_id)
        for card in cards:
            print '-----'*30
            print u'ID: {0}, DESC: {1}, NAME: {2}'.format(card['id'], card['desc'], card['name'])
            print '-----' * 30

    #
# {u'labels': [], u'pos': 131071.5, u'manualCoverAttachment': False,
#  u'id': u'5749f2ba61212cc617266535',
#  u'badges': {
#      u'votes': 0, u'attachments': 0, u'subscribed': False, u'due': None,
#      u'comments': 3, u'checkItemsChecked': 0, u'fogbugz': u'',
#      u'viewingMemberVoted': False, u'checkItems': 0, u'description': True},
#  u'idBoard': u'5749cb8abae57c61049494c0', u'idShort': 5, u'due': None,
#  u'shortUrl': u'https://trello.com/c/FM2mlpJ7', u'closed': False,
#  u'subscribed': False, u'dateLastActivity': u'2016-06-20T18:42:43.246Z',
#  u'idList': u'5749cb9248beffd4ee09fcb3', u'idMembersVoted': [],
#  u'idLabels': [], u'idMembers': [u'574c54824a5f7ff442160ae3'],
#  u'checkItemStates': None,
#  u'desc': u'1 qa c\u0435\u0440\u0432\u0435\u0440 - \u0434\u043b\u044f \u0442\u0435\u0441\u0442\u043e\u0432 \u043d\u0430\u0434 \u0433\u043e\u0442\u043e\u0432\u044b\u043c\u0438 \u0442\u0430\u0441\u043a\u0430\u043c\u0438\n2 \u0434\u0435\u0432-\u0441\u0435\u0440\u0432\u0435\u0440\u0430 - \u043c\u043e\u0436\u043d\u043e \u043b\u0438 \u0441\u0434\u0435\u043b\u0430\u0442\u044c \u0442\u0430\u043a, \u0447\u0442\u043e\u0431\u044b \u043f\u0440\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u0438 \u043a\u0430\u0436\u0434\u044b\u0439 \u043c\u043e\u0433 \u0441\u043e\u0431\u0440\u0430\u0442\u044c \u043d\u0430 \u043a\u043e\u043d\u043a\u0440\u0435\u0442\u043d\u043e\u043c \u0441\u0435\u0440\u0432\u0430\u043a\u0435 \u0438\u0437 \u044d\u0442\u0438\u0445 \u0434\u0432\u0443\u0445 \u0441\u0432\u043e\u044e \u043b\u0438\u0447\u043d\u0443\u044e \u0432\u0435\u0442\u043a\u0443 \u0434\u043b\u044f \u043f\u043e\u0433\u043e\u043d\u044f\u0442\u044c', u'descData': {u'emoji': {}}, u'name': u'\u0440\u0430\u0441\u043a\u043b\u0430\u0434\u043a\u0430 \u043f\u043e \u0441\u0435\u0440\u0432\u0430\u043a\u0430\u043c \u0434\u043b\u044f \u043f\u0440\u043e\u0434\u043a\u0443\u0442\u043e\u0432',
#  u'shortLink': u'FM2mlpJ7', u'idAttachmentCover': None,
#  u'url': u'https://trello.com/c/FM2mlpJ7/5--', u'idChecklists': []}