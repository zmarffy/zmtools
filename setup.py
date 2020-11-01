import re
from os.path import join as join_path

import setuptools

with open(join_path("zmtools", "__init__.py"), encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setuptools.setup(
    name='zmtools',
    version=version,
    author='Zeke Marffy',
    author_email='zmarffy@yahoo.com',
    packages=setuptools.find_packages(),
    url='https://github.com/zmarffy/zmtools',
    license='MIT',
    description='Various tools used across Zeke Marffy\'s programs',
    python_requires='>=3.8',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    install_requires=[
        "getch",
        "packaging"
    ],
)
