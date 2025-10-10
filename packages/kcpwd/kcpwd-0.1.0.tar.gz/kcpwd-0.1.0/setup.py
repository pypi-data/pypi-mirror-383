from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kcpwd",
    version="0.1.0",
    author="osmanuygar",
    author_email="osmanuygar@gmail.com",
    description="macOS Keychain Password Manager CLI - Simple and secure password storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osmanuygar/kcpwd",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS",
    ],
    keywords="password manager cli keychain macos security",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "keyring>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "kcpwd=kcpwd.cli:cli",
        ],
    },
)