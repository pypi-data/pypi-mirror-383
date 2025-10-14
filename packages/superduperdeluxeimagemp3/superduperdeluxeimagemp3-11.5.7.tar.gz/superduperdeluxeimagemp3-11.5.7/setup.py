from setuptools import setup, find_packages

setup(
    name='sddimp3tools',
    version='11.5.7',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'SDDIMP3 = SDDIMP3.SDDIMP3:main',
            'SDDIMP3playlisthelper = SDDIMP3.SDDIMP3playlisthelper:main',
        ],
    },
    install_requires=[
            'yt-dlp',
            'pillow',
            'moviepy',
        ],
)
