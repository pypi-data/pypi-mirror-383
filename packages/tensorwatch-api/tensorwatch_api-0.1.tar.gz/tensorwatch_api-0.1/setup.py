from setuptools import setup, find_packages

setup(
    name='tensorwatch-api',
    version='0.1',
    packages=['twapi'],
    install_requires=[
        'pykafka',
        'tensorwatchext',
        'ipywidgets',
        'ipympl',
    ],
    entry_points={
        'console_scripts': [
            'twapi-senter=twapi.Example_Senter:main',
        ],
    },
)
