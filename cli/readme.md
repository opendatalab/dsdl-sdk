# 初始化python virtualenv基本环境

```shell
    python -m venv py38 # 创建一个虚拟环境，其他工具也可以
    py38\Scripts\activate
    pip install -r requirements-dev.txt
    pre-commit install  #执行一下，初始化pre-commit环境
```

## requirements-dev.txt 里包含了3个工具

1. poetry 管理python第三方依赖库+打包+发布到pypi
2. tox 本地python版本兼容性测试+运行单元测试代码
3. pre-commit 代码提交前的代码格式化+代码检查，发生在开发者本地执行git commit之前，会做一些风格和规范检查，如果不通过，会阻止提交并给出提示

以上环境安装一次就可以了。**如果是windows环境需要安装gitforwindows, cygwin等自带的运行会报错**

## poetry依赖管理

## tox单元测试
