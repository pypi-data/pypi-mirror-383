# setup.py

from setuptools import setup, find_packages

setup(
    name='trojanrat-ai-scripts',
    version='0.2.0', 
    author='trojanrat',
    description='A tool to place a collection of AI scripts into your current project folder.',
    
    packages=find_packages(),
    
    # This makes sure 'all_ai_scripts.txt' is included
    package_data={
        'trojanrat_scripts': ['all_ai_scripts.txt'],
    },
    
    # This creates the command 'get-ai-scripts'
    entry_points={
        'console_scripts': [
            'get-ai-scripts = trojanrat_scripts.cli:main',
        ],
    },
)