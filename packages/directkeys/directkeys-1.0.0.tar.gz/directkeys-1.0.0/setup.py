"""
Usage instructions:

- If you are installing: `python setup.py install`
- If you are developing: `python setup.py sdist bdist_wheel && twine check dist/*`
"""
import directkeys

from setuptools import setup

setup(
    name='directkeys',
    version=directkeys.version,
    author='WigoWigo',
    author_email='hiigoor93@gmail.com',
    packages=['directkeys'],
    url='https://github.com/WigoWigo10/keyboard',
    license='MIT',
    description='A modern and robust keyboard hooking and simulation library for Windows and Linux, focusing on low-level control.',
    keywords='directkeys keyboard hook simulate hotkey low-level win32 sendinput',
    long_description=directkeys.__doc__.replace('\r\n', '\n'),
    long_description_content_type='text/markdown',
    install_requires=["pyobjc; sys_platform=='darwin'"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)