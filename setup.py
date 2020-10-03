import setuptools

setuptools.setup(
    name='zmtools',
    version='1.0.1',
    author='Zeke Marffy',
    author_email='zmarffy@yahoo.com',
    packages=setuptools.find_packages(),
    url='https://github.com/zmarffy/zmtools',
    license='LICENSE.txt',
    description='Various tools used across Zeke Marffy\'s programs',
    python_requires='>=3.8',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    install_requires=[
        "getch"
    ],
)