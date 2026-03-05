from setuptools import setup, find_packages

setup(
    name="pystorageops",
    version="1.0.0",
    description="Storage management, monitoring, and automation toolkit",
    author="PyStorageOps Contributors",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.3",
        "pyyaml>=6.0.1",
        "protobuf>=4.25.2",
        "prometheus-client>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "httpx>=0.26.0",
            "ruff>=0.1.14",
        ],
    },
)
