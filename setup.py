from setuptools import setup, find_namespace_packages
import json

with open('lmctl/pkg_info.json') as fp:
    _pkg_info = json.load(fp)

setup(
    name='lmctl',
    version=_pkg_info['version'],
    packages=find_namespace_packages(include=['lmctl*']),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'ruamel.yaml',
        'oyaml',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        lmctl=lmctl.cli.entry:init_cli
    '''
)
