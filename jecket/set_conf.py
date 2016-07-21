import logging

conf_file = '/etc/jecket/jecket.conf'

logger = logging.getLogger(__name__)


def main(args):
    with open(conf_file, 'w') as f:
        f.write('{0}\n'
                '{1}\n'
                '{2}\n'.format(args.base_link, args.username, args.password))
    logger.info('Configuration file has been created.')


if __name__ == '__main__':
    main()
