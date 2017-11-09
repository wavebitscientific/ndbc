from setuptools import setup

setup(
    name='ndbc',
    version='0.1.0',
    description='Python interface to NDBC data',
    author='Milan Curcic',
    author_email='mcurcic@wavebitscientific.com',
    url='https://github.com/wavebitscientific/ndbc',
    packages=['ndbc'],
    install_requires=['numpy', 'requests'],
    test_suite='ndbc.tests',
    license='MIT'
)
