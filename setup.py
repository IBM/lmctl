from setuptools import setup, find_packages

setup(
    name='lmctl',
    version='2.0.8dev0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'paramiko',
        'urllib3',
        'oyaml',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        lmctl=lmctllib.installer:main_func
    ''',
)
