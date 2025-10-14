from setuptools import setup, find_packages

setup(
    name='gxl_ai_utils',
    version='1.5.3',
    author='Xuelong Geng',
    description='这个是耿雪龙的工具包模块, update time: 2025-10-13',
    author_email='3349495429@qq.com',
    packages=find_packages(where='gxl_ai_utils'),  # 仅安装gxl_ai_utils目录下的包
    install_requires=[  # 安装依赖库
        'jsonlines',
        'colora',
        'tqdm',
    ],
    package_dir={'': 'gxl_ai_utils'},  # 确保安装时是从gxl_ai_utils目录下找包
)
