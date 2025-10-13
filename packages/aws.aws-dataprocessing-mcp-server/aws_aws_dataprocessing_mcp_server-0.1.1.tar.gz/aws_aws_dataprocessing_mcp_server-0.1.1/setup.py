from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

class PostInstallCommand(install):
    """Post-installation script to create the file."""
    def run(self):
        install.run(self)
        # Create the file after installation
        try:
            home_dir = Path.home()
            file_path = home_dir / "Hey_from_mainteemo"
            with open(file_path, 'w') as f:
                f.write("Hello from aws-dataprocessing-mcp-server!\n")
                f.write("This file was created automatically upon installation.\n")
            print(f"\n✓ File created at: {file_path}\n")
        except Exception as e:
            print(f"\n✗ Error creating file: {e}\n")

setup(
    name="aws.aws-dataprocessing-mcp-server",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package that creates a file in the home directory upon installation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aws-dataprocessing-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        "console_scripts": [
            "aws.aws-dataprocessing-mcp-server=aws.aws_dataprocessing_mcp_server.main:main",
            "aws-dataprocessing-mcp=aws.aws_dataprocessing_mcp_server.main:main",
        ],
    },
)
