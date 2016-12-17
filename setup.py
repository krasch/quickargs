from setuptools import setup
import pypandoc

long_description = pypandoc.convert('README.md', 'rst')

setup(
    name='quickargs',
    version='0.1',
    packages=['quickargs'],
    url='https://github.com/krasch/quickargs',
    license='MIT',
    author='krasch',
    author_email='code@krasch.io',
    description='YAML config file -> command line interface',
    long_description=long_description,
    install_requires=['pyyaml>=3.10'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',],
    test_suite='nose.collector',
    tests_require=['nose'],

)
