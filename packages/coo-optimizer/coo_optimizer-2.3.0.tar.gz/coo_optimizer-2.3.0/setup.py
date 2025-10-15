from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()
                    and not line.startswith("#")]

setup(
    name="coo_optimizer",
    version="2.3.0",
    author="Sandip Garai",
    author_email="sandipnicksandy@gmail.com",
    description="Canine Olfactory Optimization - A bio-inspired metaheuristic algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SandipGarai/coo_optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=6.0", "pytest-cov>=2.0", "black>=21.0", "flake8>=3.9"],
    },
    keywords="optimization, metaheuristic, hyperparameter-tuning, machine-learning, evolutionary-algorithm",
    project_urls={
        "Bug Reports": "https://github.com/SandipGarai/coo_optimizer/issues",
        "Source": "https://github.com/SandipGarai/coo_optimizer",
        "Documentation": "https://coo_optimizer.readthedocs.io",
    },
)
