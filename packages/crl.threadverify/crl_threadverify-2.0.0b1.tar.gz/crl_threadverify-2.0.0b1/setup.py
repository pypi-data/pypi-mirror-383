import os
import importlib.util
from setuptools import setup, find_packages
__copyright__ = 'Copyright (C) 2019, Nokia'


VERSIONFILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'src', 'crl', 'threadverify', '_version.py')


def get_version():
    spec = importlib.util.spec_from_file_location('_version', VERSIONFILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_version()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='crl.threadverify',
    version=get_version(),
    author='Petri Huovinen',
    author_email='petri.huovinen@nokia.com',
    description='Robot Framework thread management verification library',
    install_requires=['future'],
    long_description=read('README.rst'),
    license='BSD-3-Clause',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.12',
                 'Topic :: Software Development'],
    keywords='robotframework thread',
    url='https://github.com/nokia/crl-threadverify',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['crl'],
)
