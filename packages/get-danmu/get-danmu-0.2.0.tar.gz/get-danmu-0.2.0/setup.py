import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="get-danmu",
    version="0.2.0",
    author="Li Zhan Qi",
    author_email="3101978435@qq.com",
    description="可以下载弹幕的包哦",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=["requests",'rich','ujson','flask','flask_sqlalchemy'
                      ,'sqlalchemy','protobuf','xmltodict'],
    entry_points={
        'console_scripts': ["get-danmu=get_danmu.__main__:main",
                            "get-dm=get_danmu.__main__:main"
            ],
    },
)
