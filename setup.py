import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'BeautifulSoup',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='outages',
      version='0.0',
      description='outages',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Greg Jurman',
      author_email='gdj2214@rit.edu',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='outages',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = outages:main
      [console_scripts]
      initialize_outages_db = outages.scripts.initializedb:main
      scrape_outages_data = outages.scripts.runscraper:main
      geofix_outages_data = outages.scripts.geofix:main
      """,
      )
