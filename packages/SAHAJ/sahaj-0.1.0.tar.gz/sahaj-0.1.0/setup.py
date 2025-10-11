from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import time

class CustomInstallCommand(install):
    def run(self):
        print("Starting Sahaj installation...")
        total_steps = 10
        for i in range(total_steps):
            time.sleep(0.2)  # Simulate work
            progress = (i + 1) / total_steps * 100
            print(f"[{'#' * (i + 1)}{'-' * (total_steps - i - 1)}] {progress:.0f}%", end='\r')
        print("\n")
        install.run(self)
        print(r"""
   _____       _           _
  / ____|     | |         | |
 | (___   __ _| |__   __ _| |
  \___ \ / _` | '_ \ / _` | |
  ____) | (_| | |_) | (_| | |
 |_____/ \__,_|_.__/ \__,_|_|

""")
        print("Sahaj installed successfully!")

setup(
    name='SAHAJ',
    version='0.1.0',
    packages=find_packages(),
    cmdclass={
        'install': CustomInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'SAHAJ=sahaj.__main__:main',
        ],
    },
    author='Cline',
    author_email='cline@example.com',
    description='A simple pip library for Sahaj',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/sahaj',
    package_data={'sahaj': ['LICENSE.md']},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
