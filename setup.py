from setuptools import setup, find_packages

setup(
    name             = 'AutoChecker',
    version          = '1.7.0',
    description      = 'AutoChecker 1.7.0 Package for distribution',
    author           = 'simjeehoon',
    author_email     = 'simjeehoon@gmail.com',
    url              = 'https://github.com/simjeehoon/TestPack',
    download_url     = 'https://github.com/simjeehoon/TestPack/archive/master.zip',
    install_requires = ['pandas', 'openpyxl', 'styleframe'],
    packages         = find_packages(exclude = ['tests*']),
    keywords         = ['TestPack', 'testpack'],
    python_requires  = '>=3',
    package_data     =  {
        'TestPack' : [
            'testpack_configs.txt',
    ]},
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)