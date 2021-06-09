from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='lime_transport_websocket',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    version='v1.0.4',
    license='MIT',
    description='WebSocket transport class for the LIME protocol',
    author='Gabriel Santos <gabrielr@take.net>, Luis Araújo <luisc@take.net>',
    author_email='gabrielr@take.net',
    url='https://github.com/chr0m1ng/lime-transport-websocket',
    keywords=[
        'lime',
        'websocket',
        'ws',
        'wss',
        'transport'
    ],
    install_requires=[
        'lime-python',
        'websockets'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)
