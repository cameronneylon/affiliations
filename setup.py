from setuptools import setup, find_packages

setup(
        classifiers=[
            "Development Status :: 4 - Beta"
            ],
        description='Database of PLOS Article Affiliations.',
        install_requires = [
            'BeautifulSoup4',
            'peewee>=2.0.0',
            ],
        name='affiliations',
        packages=find_packages(),
        url='',
        version="0.01"
        )