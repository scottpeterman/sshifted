from setuptools import setup, find_packages

setup(
    name="sshifted",
    version="0.1.5",
    description="A python SSH multi-tabbed Terminal based on PyQt6 and FastAPI",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    url="https://github.com/scottpeterman/sshifted",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.5.0",
        "PyQt6-Qt6>=6.5.0",
        "PyQt6-sip>=13.6.0",
        "PyQt6-WebEngine>=6.5.0",
        "PyQt6-WebEngine-Qt6>=6.5.0",
        "PyYAML>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "sshifted = sshifted.__main__:main"
        ],
    },
)
