from distutils.core import setup

setup(
    name = 'glassdoor',
    version = '0.0.2',
    description = 'Glassdoor Python API Client',
    author = 'Dan Temkin',
    author_email = 'temkin.d01@gmail.com',
    packages = ['glassdoor'],
    install_requires=['requests==2.0.0'],
    url = "https://github.com/dtemkin/glassdoor-python",
)
