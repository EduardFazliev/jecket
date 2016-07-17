conf_file = 'conf.py'
conf_example = 'conf.py_example'

try:
    import conf
    assert conf
except ImportError as e:
    with open(conf_example, 'r') as f:
        with open(conf_file, 'w') as f1:
            for line in f:
                f1.write(line)
    print 'Config file is missing. Generic configuration created.'


def main(args):
    with open(conf_file, 'w') as f:
        f.write('base_api_link = "{0}"\n'
                'user = "{1}"\n'
                'passwd = "{2}"\n'.format(args.base_link,
                                          args.username, args.password))
    print('Configuration file has been created.')


if __name__ == '__main__':
    main()
