from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="lerobot_robot_bi_so101_follower",
    version="0.0.1",
    description="LeRobot so101 bimanual integration package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Leo and Keshav",
    author_email="gyattman123@gmail.com",
    url="https://github.com/SIGRobotics-UIUC/lerobot_robot_bi_so101_follower",
    project_urls={
        "Bug Tracker": "https://github.com/SIGRobotics-UIUC/lerobot_robot_bi_so101_follower/issues",
        "Documentation": "https://github.com/SIGRobotics-UIUC/lerobot_robot_bi_so101_follower#readme",
        "Source Code": "https://github.com/SIGRobotics-UIUC/lerobot_robot_bi_so101_follower",
    },
    packages=find_packages(),
    install_requires=[
        "lerobot>=1.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="robotics, lerobot, bimanual, so101",
    include_package_data=True,
    zip_safe=False,
)
