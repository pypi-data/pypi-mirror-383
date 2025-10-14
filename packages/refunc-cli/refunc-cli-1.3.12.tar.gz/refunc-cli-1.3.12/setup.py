import os
import sys
from distutils.core import setup
from setuptools import find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")
here = os.path.abspath(os.path.dirname(__file__))

setup_args = dict(
    name='refunc-cli',
    version='1.3.12',
    description='refunc command line tools',
    author='arvin',
    license='MIT',
    url='https://github.com/refunc/refunc-cli',
    author_email='arvintian8@gamil.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
    [console_scripts]
    rfctl=rfctl.__main__:cli
    ''',
)

if 'setuptools' in sys.modules:
    setup_args['zip_safe'] = False
    setup_args['install_requires'] = install_requires = []

    with open('requirements.txt', "r", encoding="utf-8") as f:
        for line in f.readlines():
            req = line.strip()
            if not req or req.startswith('#') or '://' in req:
                continue
            install_requires.append(req)


def main():
    setup(**setup_args)


if __name__ == "__main__":
    main()
