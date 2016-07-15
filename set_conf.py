import logging
import os.path


def main(args):
    logger = logging.getLogger(__name__)

    #if not os.path.isfile('conf.py'):
    with open('conf.py','w') as f:
        if args.base_link is not None:
                  f.write('base_api_link = "{0}"\n'.format(args.base_link))
        else: 
				print ('Baselink is not defined')
				f.write('base_api_link = ""\n')
        if args.username is not None:
                f.write('user = "{0}"\n'.format(args.username))
        else:
				print ('Username is not defined')
				f.write('user = ""\n')
        if args.password is not None:
                f.write('passwd = "{0}"\n'.format(args.password))
        else:
				print ('Password is not defined')
				f.write('passwd = ""\n')
        print('Configuration file has been created.')
    #else: logger.info('The file already exists!')





if __name__ == '__main__':
    main()