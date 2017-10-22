from setuptools import setup
# you may need setuptools instead of distutils

setup(
    name='PymeExeterSiteconfig',
    version='0.1',
    description='Site specific files for PYME - Univ. Exeter Soeller Lab',
    url='http://bitbucket.org/christian_soeller/pyme-exeter-siteconfig',
    author='Christian Soeller and Lab Members',
    author_email='c.soeller@gmail.com',
    license='GPL',
    scripts = [
        'scripts/PYMEConfig.py'
    ]
)
