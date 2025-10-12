from setuptools import setup, find_packages

setup(
    name='sinlang',
    version='1.1.0',
    author='sin',
    description='A programming language combining Python printing with C++ control flow.',
    url='https://github.com/sin860/SinLang-Interpreter.git',
    packages=find_packages(),
    install_requires=[
        'lark-parser>=0.11.0',
    ],
    include_package_data=True,
    package_data={
        'sinlang': ['sin_grammar.lark'],
    },
    entry_points={
        'console_scripts': [
            'sinlang = sinlang.cli:main',
        ],
    },
)
