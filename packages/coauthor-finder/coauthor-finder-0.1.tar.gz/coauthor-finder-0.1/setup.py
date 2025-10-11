from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='coauthor-finder',
    version='0.1',
    license='CC BY-NC-SA',
    author='Chen Liu',
    author_email='chen.liu.cl2482@yale.edu',
    packages={'coauthor_finder'},
    # package_dir={'': ''},
    description='A simple tool to list all your coauthors and the year of lastest collaboration.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ChenLiu-1996/CoauthorFinder',
    keywords='coauthor, google scholar',
    install_requires=['scholarly', 'tqdm', 'pandas'],
    classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'License :: Other/Proprietary License', # Again, pick a license
    'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
    ],
)