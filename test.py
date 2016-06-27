import sys

# from pull_request_file_comments import SendResultsToPullRequestFiles
from pull_request_main_comments_section import PullRequestCommits
#
#
def main():
    # test_trello = TrelloCollector()
    # list_of_lists = test_trello.get_board_lists('J8SCc9EX')
    # for lst in list_of_lists:
    #     print lst[0]
    #     test_trello.get_lists_cards(lst[1])
    #     print 30*'#####'

    #test_trello.get_lists_cards('5749cb9248beffd4ee09fcb3')
    #print test_trello.get_card_info('5749f2ba61212cc617266535')
    #print test_trello.get_card_info('5749cba3cda22044015dd53a')
#     pr_test = SendResultsToPullRequestFiles(
#         base_api_link="http://bitbucket.infotech.team/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
#         checked_file='testj/test.java',
#         username='jenkins',
#         passwd='jenkins'
#     )
# #    print pr_test.send_static_check_results()
#
#     pr = SendResultsToPullRequest(
#         base_api_link="http://bitbucket.infotech.team/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
#         username='jenkins',
#         passwd='jenkins',
#         base_build_status_link="http://bitbucket.infotech.team/rest/build-status/1.0/commits/"
#     )
#     print pr.send_build_status('FAILED', 'somekey', 'http://jenkins.infotech.team')
#
    pr = PullRequestCommits(
        base_api_link="http://bitbucket.infotech.team/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
        username='jenkins',
        passwd='jenkins'
    )
    for commit_id in pr.get_commits()[0]:
        sys.stdout.write(commit_id+',')


if __name__ == '__main__':
    main()
