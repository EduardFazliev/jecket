import logging

conf_file = 'conf.py'
conf_example = 'conf.py_example'

logger = logging.getLogger(__name__)


try:
    import conf
    assert conf
except ImportError as e:
    logging.exception('Error occurred while importing conf: {}.'.format(e))
    with open(conf_example, 'r') as input_file:
        with open(conf_file, 'w') as output_file:
            for line in input_file:
                output_file.write(line)
    print 'Configuration file is missing. Generic configuration has been created.'
    import conf


def main(args):
    with open(conf_file, 'w') as f:
        f.write('base_api_link = "{0}"\n'
                'user = "{1}"\n'
                'passwd = "{2}"\n'.format(args.base_link, args.username, args.password))
    print('Configuration file has been created.')


if __name__ == '__main__':
    main()
