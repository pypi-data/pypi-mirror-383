from setuptools import setup, find_packages

setup(
    name="moo_printer",  # Replace with your desired package name
    version="1.2.0",  # Initial version
    author="Your Name",
    author_email="your_email@example.com",
    description="A simple package that prints 'moo'",
    long_description="A simple Python package that prints 'moo' when executed.",
    long_description_content_type="text/plain",
    url="https://github.com/yourusername/moo_printer",  # Replace with your GitHub repo URL (optional)
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)