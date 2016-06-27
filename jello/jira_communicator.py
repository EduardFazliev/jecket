import jira


class JiraCommunicator(object):
    def __init__(self, jira_url, login, passwd, prj_key):
        self.jira_url = jira_url
        self.prj_key = prj_key
        self.jira_connect = jira.JIRA(jira_url, basic_auth=(login, passwd))

    def create_issue(self, summary, ):
        pass



