import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="athenanewsapi",               # Package name
    version="0.1.0",                    # Initial release version
    author="Matt F.",   
    author_email="matt@runathena.com",
    description="A simple wrapper for the Athena News API to simplify searching for articles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/athenanewsapi/athenanews",  # Update with your repo URL
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)