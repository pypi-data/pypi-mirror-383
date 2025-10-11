from setuptools import setup, find_packages

setup(
    name="siqa_hash",  # This is the package name
    version="0.1.0",
    author="Your Name",
    description="Simplified Quantum Hash (SIQA) using Qiskit",
    packages=find_packages(),  # Automatically find siqa_hash package
    install_requires=[
        "qiskit",
        "numpy"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "siqa-hash=siqa_hash.siqa_hashcode:main"  # Optional: CLI command
        ]
    },
)
