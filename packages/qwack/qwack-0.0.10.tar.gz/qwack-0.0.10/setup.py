#!/usr/bin/env python
"""Distutils setup script."""
import os
import setuptools

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='qwack',
    version='0.0.10',
    install_requires=['pyyaml', 'blessed'],
    long_description=open(os.path.join(HERE, 'README.rst')).read(),
    description='a rogue-like game of mysterious origins!',
    author='Jeff Quast',
    author_email='contact@jeffquast.com',
    license='MIT',
    packages=['qwack', 'qwack.dat'],
    # just add the tilesets and world.yaml for now ..
    package_data={"dat": ["*.zip", "*.yaml", "*.ULT", "*.MAP", "*.ega"]},
    url='https://github.com/jquast/qwack',
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'qwack = qwack:main.main',
        ] }
)
