from setuptools import setup, find_packages
import proxyutils

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name=proxyutils.__title__,
    version=proxyutils.__version__,
    author=proxyutils.__author__,
    url="https://github.com/meliksahbozkurt/proxyutils",
    description="Proxy string to python-compatible dictionary converter.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license=proxyutils.__license__,
    packages=find_packages(),
    package_data={"proxyutils": ["dist.*"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "proxyutils = proxyutils.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.9",
)
