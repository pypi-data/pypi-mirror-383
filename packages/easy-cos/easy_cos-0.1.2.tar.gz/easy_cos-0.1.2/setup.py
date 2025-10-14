from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8") if (this_dir / "README.md").exists() else ""

setup(
    name="easy_cos",       # 库的名称
    version="0.1.2",      # 版本号
    author="Jiaqi Wu",
    description="A simple wrapper for cos",  # 描述
    long_description=open("README.md", "r", encoding="utf-8").read(),  # 长描述，从README.md读取<e
    long_description_content_type="text/markdown",  # 长描述的格式，这里是markdown<e
    packages=find_packages(),  # 自动找到所有包
    install_requires=[  
        'cos-python-sdk-v5',
        "tqdm",
        "pillow",
        "numpy",
    ],
    classifiers=[  # 可选，帮助别人找到你的库
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.8",
)