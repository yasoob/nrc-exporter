import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    REQUIRES = [line.strip() for line in fh.readlines()]

setuptools.setup(
    name="nrc-exporter",
    version="0.0.2",
    author="Yasoob Khalid",
    author_email="hi@yasoob.me",
    description="This program allows you to export your runs from Nike Run Club and convert them in GPX format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yasoob/nrc-exporter",
    install_requires=REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.4",
    py_modules=["nrc_exporter"],
    entry_points={"console_scripts": ["nrc-exporter = nrc_exporter:main"]},
)
