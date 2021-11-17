from setuptools import setup, find_packages

setup(
    name             = 'AutoChecker',
    version          = '1.0.0',
    description      = 'AutoChecker 1.0.0 Package for distribution',
    author           = 'simjeehoon',
    author_email     = 'simjeehoon@gmail.com',
    url              = 'https://github.com/simjeehoon/AutoChecker',
    download_url     = 'https://github.com/simjeehoon/AutoChecker/archive/master.zip',
    install_requires = ['pandas', 'openpyxl', 'styleframe'],
    packages         = find_packages(),
    keywords         = ['AutoChecker', 'autoChecker', 'auto_checker'],
    python_requires  = '>=3',
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)