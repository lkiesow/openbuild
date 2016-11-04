from setuptools import setup

setup(
    name='openbuild',
    version='1.0',
    description='Build server for git',
    author='Lars Kiesow',
    author_email='lkiesow@uos.de',
    license='AGPLv3',
    url='https://github.com/lkiesow/openbuild',
    packages=['openbuild'],
    install_requires=[
        'sqlalchemy>=0.9.8',
        'PyYAML'
    ],
    scripts=[
        'openbuild-add',
        'openbuild-list',
        'openbuild-run'
    ]
)
