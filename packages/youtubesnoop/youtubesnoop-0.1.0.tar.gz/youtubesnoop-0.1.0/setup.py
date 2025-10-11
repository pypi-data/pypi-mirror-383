"""Setup configuration for YoutubeSnoop."""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements = Path('requirements.txt').read_text().strip().split('\n')

# Read version from package
version = {}
with open('youtube_snoop/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)

setup(
    name='youtube-snoop',
    version=version.get('__version__', '0.1.0'),
    description='YouTube video/music downloader with metadata tagging',
    author='Anders',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'youtubesnoop=youtube_snoop.cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
