from setuptools import setup, find_packages

setup(
    name="lerobot_teleoperator_bi_so101_leader",
    version="0.0.1",
    description="LeRobot XArm integration",
    author="Leo and Keshav",
    author_email="garbage@spes.ai",
    packages=find_packages(),
    install_requires=[
        "teleop",
        "lerobot",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
)
