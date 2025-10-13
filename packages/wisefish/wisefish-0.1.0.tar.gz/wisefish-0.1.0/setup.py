from setuptools import setup, find_packages

setup(
    name="wisefish",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # ensures package_data is included
    package_data={"wisefish": ["default_config.json"]},  # include the default config
    install_requires=[
        "platformdirs>=3.0"  # add platformdirs as a dependency
    ],
    entry_points={
        "console_scripts": [
            "wisefish=wisefish.cli:main",  # command users will type
        ],
    },
    python_requires=">=3.8",
)
