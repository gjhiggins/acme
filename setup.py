import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'requests',
    'waitress',
    'rdflib',
    'pyqrcode'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
    'lxml',
    'json_schema_generator',
]

setup(
    name='acme',
    version='0.0',
    description='ACME, A Cryptocurrency Metadata Explorer - and a LOD endpoint and publisher.',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],

    author="Graham Higgins",
    author_email="gjhiggins@gmail.com",
    url="https://github.com/gjhiggins/acme",
    license="BSD",
    platforms=["any"],
    keywords='web wsgi pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='acme',
    install_requires=requires,
    extras_require={
        'testing': tests_require,
    },
    entry_points={
        'paste.app_factory': ['main = acme:main']
    },
)
