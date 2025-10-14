from setuptools import setup, find_packages

setup(
    name="bjtube",
    version="1.0.0",
    author="Babar Ali Jamali",
    author_email="babar995@gmail.com",
    description="A YouTube downloader with faster speed, ffmpeg is essential to use before installation. with auto-update and dependency installer.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/babaralijamali/bjtube",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "bjtube = bjtube.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    license="MIT",
)
