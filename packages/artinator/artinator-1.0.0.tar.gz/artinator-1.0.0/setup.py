from setuptools import setup


setup(
    name='artinator',
    versioning='dev',
    setup_requires='setupmeta',
    install_requires=[
        'cli2',
        'litellm',
    ],
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://github.com/yourlabs/artinator',
    include_package_data=True,
    license='MIT',
    keywords='cli',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'artinator = artinator.cli:cli.entry_point',
        ],
    },
)
