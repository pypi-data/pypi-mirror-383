from setuptools import setup, find_packages

setup(
    name="dockai",
    version="0.5.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
        "click>=8.1,<9.0",
        "docker>=6.1,<7.0",          # Docker SDK for Python
        "openai>=1.0,<2.0",          # yeni OpenAI Python SDK
        "requests>=2.31,<3.0",
        "termcolor>=2.0,<3.0",
        "fastapi>=0.110,<1.0",       # FastAPI 1.0 çıktığında manuel değerlendirin
        "uvicorn>=0.23,<1.0",
        "stripe>=9,<10",             # stripe-python 9.x güvenli aralık
        "python-dotenv>=1.0,<2.0",
        "PyJWT>=2.0,<3.0",
    ],
    extras_require = {
        "cloud": ["openai>=1.0,<2.0", "stripe>=9,<10"],
        "dev": ["pytest", "black", "ruff", "pip-tools"],
    },
    entry_points={
        "console_scripts": [
            "dockai=dockai.cli.commands:cli",
        ],
    },
    author="Ahmet Atakan",
    author_email="ahmetatakan.tech@gmail.com",
    description="DockAI – AI-powered Docker Log Analysis Tool (CLI + Cloud)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    python_requires=">=3.9",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring",
    ],
)
