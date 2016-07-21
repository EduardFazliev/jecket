conf_file = '/tmp/jecket/jecket.conf'


def main(args):
    with open(conf_file, 'w') as f:
        f.write('{0}\n'
                '{1}\n'
                '{2}\n'.format(args.base_link, args.username, args.password))
    print 'Configuration file has been created.'


if __name__ == '__main__':
    main()
