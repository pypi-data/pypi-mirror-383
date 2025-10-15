from setuptools import find_packages, setup

setup(
    name="ventrun",
    version="1.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ventrun=ventrun.cli:main",
        ],
    },
    python_requires=">=3.13",
    install_requires=[
        "loguru>=0.5.0",  # 根据你的实际依赖调整
    ],
    author="Joxos",
    author_email="xujunhao61@163.com",
    description="Bootstrap your application and emit a Main event to ModuVent.",
    keywords="event-driven main entry moduvent",
    url="https://github.com/Joxos/ventrun",
)
