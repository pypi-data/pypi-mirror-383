from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="LLMEvaluationFramework",
    version="0.0.21",
    author="Sathishkumar Nagarajan",
    author_email="mail@sathishkumarnagarajan.com",
    description="Enterprise-Grade Python Framework for Large Language Model Evaluation & Testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isathish/LLMEvaluationFramework",
    project_urls={
        "Bug Tracker": "https://github.com/isathish/LLMEvaluationFramework/issues",
        "Documentation": "https://isathish.github.io/LLMEvaluationFramework/",
        "Source": "https://github.com/isathish/LLMEvaluationFramework",
    },
    packages=find_packages(),
    install_requires=[
        "typing-extensions>=4.0.0",
        "dataclasses>=0.6; python_version < '3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "mkdocs>=1.4",
            "mkdocs-material>=8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-eval=llm_evaluation_framework.cli:main",
        ],
    },
    keywords=[
        "llm", "evaluation", "testing", "benchmarking", "ai", "ml", 
        "machine-learning", "natural-language-processing", "nlp",
        "language-models", "openai", "gpt", "anthropic", "claude"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8',
)
