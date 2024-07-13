from setuptools import setup, find_packages

setup(
    name="stormy",
    version="0.1",
    description='A simple and user friendly CLI to interact with your Lego Mindstorms NXT 2.0 Brick',
    author='Hicham Terkiba',
    author_email='hicham@terkiba.com',
    packages=find_packages(),
    url='https://github.com/iobreaker/stormy',
    install_requires=[
        'rich', 'typer', 'nxt-python', 'pathlib', 'setuptools'
    ],
    entry_points={
        'console_scripts': [
            'stormy=stormy.main:app',
        ],
    },
)
