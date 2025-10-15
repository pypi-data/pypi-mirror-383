from setuptools import setup, find_packages

setup(
    name="logpulses",
    version="0.1.2",
    description="Comprehensive request/response logging middleware for FastAPI with zero configuration",
    author="Hariharan S",
    author_email="hvasan59@gmail.com",
    url="https://github.com/Hari-vasan/logpulses",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["fastapi>=0.100.0", "starlette>=0.27.0", "psutil>=5.9.0"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
    ],
    keywords="fastapi logging middleware request-logging api-logging monitoring observability",
    project_urls={
        "Homepage": "https://github.com/Hari-vasan/logpulses",
        "Documentation": "https://github.com/Hari-vasan/logpulses#readme",
        "Repository": "https://github.com/Hari-vasan/logpulses",
        "Bug Tracker": "https://github.com/Hari-vasan/logpulses/issues",
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
)
