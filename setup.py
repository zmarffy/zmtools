import setuptools

setuptools.setup(
    name='zmtools',
    version='1.1.0',
    author='Zeke Marffy',
    author_email='zmarffy@yahoo.com',
    packages=["zmtools"],
    url='https://github.com/zmarffy/zmtools',
    license='MIT',
    description='Various tools used across Zeke Marffy\'s programs',
    python_requires='>=3.8',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    install_requires=[
        "getch"
    ],
)