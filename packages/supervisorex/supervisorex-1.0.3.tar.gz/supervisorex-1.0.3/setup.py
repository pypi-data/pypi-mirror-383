from setuptools import setup, find_packages

setup(
    name="supervisorex",
    version="1.0.3",
    author="@NacDevs",
    author_email="yuvrajmodz@gmail.com",
    description="Simple CLI to create supervisor processes easily",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yuvrajmodz/supervisorex",
    packages=find_packages(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'supervisorex=supervisorex.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)

