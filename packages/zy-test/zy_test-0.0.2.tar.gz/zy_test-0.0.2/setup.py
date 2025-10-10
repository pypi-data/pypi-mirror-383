import os
from contextlib import contextmanager
from setuptools import setup, find_packages


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def _setup():
    with cd(PROJECT_DIR):
        # specify additional required packages
        install_requires = [
            # for this particular package
            # no need to specify as gptsre platform already have it
            # 'gptsre-tools',
            # 'mysql-connector-python'
        ]
        setup(
            name='zy-test',
            version='0.0.2',
            author='Shopee',
            author_email='zhuo.xu@shopee.com',
            description='SeaTalk GPTSRE Tools',
            url='https://git.garena.com/seatalk/cross-platform/ai',
            packages=find_packages(),
            install_requires=install_requires,
            package_data={
                'zy_test': [
                    'zy_test/*',
                ],
            },
            include_package_data=True,
        )


if __name__ == '__main__':
    _setup()
