from setuptools import setup, find_packages

setup(
    name='funcacher',
    version='0.1',
    description='function decorator that caches return value for the same arguments',
    author='Yen, Tzu-Hsi',
    author_email='joseph.yen@gmail.com',
    license='GPL',
    url='https://github.com/d2207197/funcacher',
    packages=find_packages(),
    install_requires=['boltons', 'pymemcache', 'msgpack-python'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-timeout'])
