from setuptools import find_packages, setup

setup(
    name="morpheus",
    packages=find_packages(include=["morpheus*"]),
    version="0.1.0",
    description="Morpheus library for delta G prediction",
    author="Elias Rusch",
    install_requires=["rdkit", "termcolor", "colored"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
    entry_points={"console_scripts": ["morpheus=morpheus.__main__:main"]},
)
