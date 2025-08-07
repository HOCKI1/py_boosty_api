from setuptools import setup, find_packages

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='PyBoostyApi',
    version='1.0.5',
    author='HOCKI1',
    author_email='hocki1.official@yandex.ru',
    description='PyBoostyAPI is a powerful asynchronous Python library for seamless interaction with the Boosty.to API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HOCKI1/py_boosty_api',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'requests',
        'beautifulsoup4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Source': 'https://github.com/HOCKI1/py_boosty_api',
        'Tracker': 'https://github.com/HOCKI1/py_boosty_api/issues',
    },
    keywords='boosty api async aiohttp donations subscribers',
    python_requires='>=3.7',
)
