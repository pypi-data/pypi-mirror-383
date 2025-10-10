# setup.py 是一个 setuptools 的构建脚本，其中包含了项目和代码文件的信息
# 如果没有需要先安装，pip install setuptools
import setuptools

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
# long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    # 项目的名称 一般在同级目录中有个同名的文件夹
    name="wcommon",
    # 项目的版本
    version="2.6.5",
    # 项目的作者
    author="WangJunbo",
    # 作者的邮箱
    author_email="wjbhnu@gmail.com",
    # 项目描述
    description="常用工具类方法集合",
    # 项目的长描述
    long_description=long_description,
    # 以哪种文本格式显示长描述
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "wtip=wcommon.__main__:main",  # 命令行工具
            "wli=wcommon.__li__:main",  # 命令行工具
            "wmv=wcommon.__init__:temp_delete_file",  # 命令行工具
            "wbk=wcommon.__init__:backup_file",  # 命令行工具
            "wcat=wcommon.__init__:clear_look",  # 命令行工具
        ],
    },
    # 所需要的依赖
    install_requires=["requests", "configparser", "pymysql", "loguru","pyzmq","aiomysql","asyncio","pillow"],  # 比如["flask>=0.10"]
    # 项目主页
    url="http://www.hohode.com",
    # 项目中包含的子包，find_packages() 是自动发现根目录中的所有的子包。
    packages=setuptools.find_packages(),
    # 其他信息，这里写了使用 Python3，MIT License许可证，不依赖操作系统。
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
