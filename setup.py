from setuptools import setup, find_namespace_packages
import json

with open('lmctl/pkg_info.json') as pkg_info_file:
    _pkg_info = json.load(pkg_info_file)

with open('DESCRIPTION.md', 'r') as description_file:
    long_description = description_file.read()

setup(
    name='lmctl',
    version=_pkg_info['version'],
    author='IBM',
    description='IBM CP4NA orchestration command line tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/IBM/lmctl',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    packages=find_namespace_packages(include=['lmctl*']),
    include_package_data=True,
    install_requires=[
        'click>=7.1,<9.0',
        'requests>=2.23,<3.0',
        'ruamel.yaml>=0.16,<1.0',
        'oyaml>=0.8,<2.0',
        'tabulate>=0.8,<1.0',
        'Jinja2>=2.11,<4.0',
        'PyYAML>=5.3.0,<7.0',
        'pydantic>=2.8.0,<3.0',
        'dataclasses>=0.6; python_version < "3.7"',
        'pyjwt>=1.5.3,<3.0'
    ],
    entry_points='''
        [console_scripts]
        lmctl=lmctl.cli.entry:init_cli
    '''
)
