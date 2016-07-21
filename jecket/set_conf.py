import logging

conf_file = '/etc/jecket/conf.py'

logger = logging.getLogger(__name__)


def main(args):
    with open(conf_file, 'w') as f:
        f.write('base_api_link = "{0}"\n'
                'user = "{1}"\n'
                'passwd = "{2}"\n'.format(args.base_link, args.username, args.password))
    logger.info('Configuration file has been created.')


if __name__ == '__main__':
    main()
