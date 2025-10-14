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
            name='zzzzztest',
            version='0.0.7',
            author='admin',
            author_email='admin@qq.com  ',
            description='zzzzztest',
            url='https://github.com/123123123123/zzzzztest',
            packages=find_packages(),
            install_requires=install_requires,
            package_data={
                'zzzzztest': [
                    'zzzzztest/*',
                ],
            },
            include_package_data=True,
        )


if __name__ == '__main__':
    _setup()
