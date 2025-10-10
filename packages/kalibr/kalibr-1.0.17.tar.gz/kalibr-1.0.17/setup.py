from setuptools import setup, find_packages

setup(
    name="kalibr",
    version="1.0.17",  # bump for new upload
    author="Devon",
    author_email="hello@kalibr.systems",
    description="Kalibr SDK — integrate your SaaS or app with every major AI model using one schema.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/devon/kalibr-sdk",
    packages=find_packages(exclude=["tests*", "examples*"]),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.29.0",
        "typer>=0.12.3",
        "pydantic>=2.6.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "kalibr-connect=kalibr.kalibr_app:run"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)
