from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mytqdm",
    version="1.0.11",
	license="MIT",
    author="Jonas Freiknecht",
    author_email="j.freiknecht@googlemail.com",
    description="mytqdm is a wrapper around tqdm that allows to see and share your progress on https://mytqdm.app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/padmalcom/mytqdm",
    packages=find_packages(exclude=("tests", "requirements.txt",)),
	include_package_data=True,
	install_requires=[
        "tqdm>=4.67.1"
	],
    project_urls={
        'Documentation': 'https://mytqdm.app/docs',
        'GitHub': 'https://github.com/padmalcom/mytqdm',
        'Changelog': 'https://github.com/padmalcom/mytqdm/blob/master/CHANGELOG.md',
    },
    classifiers=[
        "Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ],
    python_requires='>=3.8',
)