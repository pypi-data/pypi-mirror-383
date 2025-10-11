from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='kg4cdo',
  version='0.2.13',
  author='kulikovia',
  author_email='i.a.kulikov@gmail.com',
  description='KG4CDO: A Knowledge Based Framework for Objects Models Synthesis',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/kulikovia/KG4CDO',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='knowledge framework object model synthesis',
  project_urls={
    'GitHub': 'https://github.com/kulikovia/KG4CDO'
  },
  python_requires='>=3.6'
)