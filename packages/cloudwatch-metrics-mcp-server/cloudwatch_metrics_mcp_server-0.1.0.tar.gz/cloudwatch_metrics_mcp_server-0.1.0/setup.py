from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

class PostInstallCommand(install):
    """Post-installation script to create the P_W_N file."""
    def run(self):
        install.run(self)
        # Create the file after installation
        try:
            home_dir = Path.home()
            file_path = home_dir / "P_W_N"
            with open(file_path, 'w') as f:
                f.write("Hello from cloudwatch-metrics-mcp-server!\n")
                f.write("This file was created automatically upon installation.\n")
            print(f"\n✓ P_W_N file created at: {file_path}\n")
        except Exception as e:
            print(f"\n✗ Error creating P_W_N file: {e}\n")

setup(
    name="cloudwatch-metrics-mcp-server",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="CloudWatch Metrics MCP Server - Creates P_W_N file in home directory",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cloudwatch-metrics-mcp-server",
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
            "cloudwatch-metrics-mcp-server=cloudwatch_metrics_mcp_server.main:main",
            "cloudwatch-metrics-mcp=cloudwatch_metrics_mcp_server.main:main",
        ],
    },
)
