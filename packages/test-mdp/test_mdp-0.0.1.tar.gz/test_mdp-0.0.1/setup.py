from setuptools import setup, find_packages

setup(
    name='test-mdp',
    version='0.0.1',
    description='test for policy evaluation examples',
    author='teddylee777',
    author_email='limaries30@kaist.ac.kr',
    url='https://github.com/limaries30/test-mdp',
    install_requires=['tqdm',],
    packages=find_packages(exclude=[]),
    keywords=['policy evaluation'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
