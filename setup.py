from setuptools import setup, find_packages


setup(
        name='jecket',
        version='0.1',
        url='http://bitbucket.infotech.team/projects/DOCM/repos/jecket/',
        license='MIT',
        author='Eduard Fazliev',
        author_email='napalmedd@gmail.com',
        packages=find_packages(),
        scripts=['bin/jecket'],
        install_requires=[
            'requests',
            'PyYAML'
        ],
        test_suite='nose.collector',
        tests_require=[
            'nose',
            'mock',
        ],
        description='Jenkins <-> BitBucket integration'
)
