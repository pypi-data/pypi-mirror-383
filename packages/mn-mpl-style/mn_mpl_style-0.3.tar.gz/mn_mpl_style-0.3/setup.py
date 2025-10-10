from setuptools import setup, find_packages

setup(
    name='mn_mpl_style',
    version='0.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['matplotlib'],
    description='A collection of custom Matplotlib styles.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Matt Nagle',
    author_email='mattnagle96@gmail.com',
    url='https://github.com/matt-nagle/mn_mpl_style',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
