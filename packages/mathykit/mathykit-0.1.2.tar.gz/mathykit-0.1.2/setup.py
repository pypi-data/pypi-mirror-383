from setuptools import setup, find_packages

setup(
    name="mathykit",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "torch>=1.9.0",
        "requests>=2.25.0",
        "tqdm>=4.64.0",
        "huggingface-hub>=0.12.0",
        "safetensors>=0.3.0",
        "regex>=2022.0.0",
        "gradio>=3.50.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=3.9",
        ],
    },
    author="MathyKit Team",
    author_email="your.email@example.com",
    description="A lightweight AI framework for using Meta/Facebook models with pure Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mathykit",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/mathykit/issues",
        "Documentation": "https://mathykit.readthedocs.io",
        "Source Code": "https://github.com/yourusername/mathykit",
    },
    keywords="ai, machine learning, nlp, meta, facebook, opt, transformers",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)