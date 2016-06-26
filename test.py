from pull_request_file_comments import SendResultsToPullRequestFiles
from pull_request_main_comments_section import SendResultsToPullRequest


def main():
    pr_test = SendResultsToPullRequestFiles(
        base_api_link="http://bitbucket.infotech.team/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
        checked_file='testj/test.java',
        username='jenkins',
        passwd='jenkins'
    )
#    print pr_test.send_static_check_results()

    pr = SendResultsToPullRequest(
        base_api_link="http://bitbucket.infotech.team/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
        username='jenkins',
        passwd='jenkins',
        base_build_status_link="http://bitbucket.infotech.team/rest/build-status/1.0/commits/"
    )
    print pr.send_build_status('FAILED', 'somekey', 'http://jenkins.infotech.team')


if __name__ == '__main__':
    main()
