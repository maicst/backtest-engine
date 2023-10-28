import setuptools
from configparser import ConfigParser

config = ConfigParser()
config.read('setup.cfg')

# Use setup() directly with configuration options
setuptools.setup(**config['metadata'], packages=setuptools.find_packages())
