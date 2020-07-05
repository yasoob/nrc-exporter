import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nrc-exporter", # Replace with your own username
    version="0.0.1",
    author="Yasoob Khalid",
    author_email="hi@yasoob.me",
    description="This program allows you to export your runs from Nike Run Club and convert them in GPX format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yasoob/nrc-exporter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)