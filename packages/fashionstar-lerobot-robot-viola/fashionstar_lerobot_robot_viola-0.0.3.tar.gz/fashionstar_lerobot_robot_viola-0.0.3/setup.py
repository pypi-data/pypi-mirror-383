from setuptools import setup, find_packages

setup(
    name="fashionstar-lerobot-robot-viola",
    version="0.0.3",
    description="LeRobot viola integration",
    author="Spes Robotics",
    author_email="contact@spes.ai",
    packages=find_packages(),
    install_requires=[
        "lerobot-motor-starai",
        "lerobot",
        "fashionstar-uart-sdk>=1.3.6"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        # 修正许可证分类器
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)