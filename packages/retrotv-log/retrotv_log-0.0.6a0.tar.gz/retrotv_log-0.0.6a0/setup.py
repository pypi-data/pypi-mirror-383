from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="retrotv_log",
    version="v0.0.6-alpha",
    description="로깅을 위한 패키지",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RetroTV",
    author_email="yjj8353@gmail.com",
    url="https://github.com/retrotv-pypi-repo/log",
    install_requires=[],
    packages=find_packages(exclude=[]),
    keywords=["retrotv", "RetroTV", "yjj8353", "log", "Log", "logging", "Logging", "pypi"],
    python_requires=">=3",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
