# 开发者环境配置

## 初始化python virtualenv基本环境

```shell
cd dsdl-sdk #进入工程目录
pip install -r requirements-dev.txt # 初始化开发环境需要的工具
pre-commit install  #执行一下，初始化pre-commit环境
```

requirements-dev.txt 里包含了3个工具

1. `poetry` 管理python第三方依赖库+打包+发布到pypi
2. `tox` 本地python版本兼容性测试+运行单元测试代码
3. `pre-commit` 代码提交前的代码格式化+代码检查，发生在开发者本地执行`git commit`之前，会做一些风格和规范检查，如果不通过，会阻止提交并给出提示

以上环境安装一次就可以了。**如果是windows环境需要安装git-for-win。 cygwin等自带的git命令结合win下的pre-commit运行会报错**
在代码仓库里和pre-commit相关的配置文件为`.pre-commit-config.yaml`, `isort.toml`，
**这样配置带来的影响是**：

如果要提交的代码import, 代码行长度，类型不明...会在git commit之前就失败并告知原因，这样代码自然也就无法push到仓库里。

## poetry 依赖管理和包发布

`poetry` 一个工具可以完成：

1. 多环境依赖管理。例如有些包在发布环境无用，但是测试、开发又必须要有。
2. 构建python源码包、whl包
3. 发布包到pypi
4. 可扩展，例如可以执行自定义命令：`poetry tox`，自动执行单元测试
5. 管理虚拟环境，类似conda。

综合来说就是集成度高，同时可以与github等无缝集成。不会造成使用pip, twine, setup.py, tox等碎片化工具带来的混乱和学习成本。

项目中与poetry相关的配置文件为`pyproject.toml`

### 1. 第三方依赖添加

传统上依赖的管理是`virtualenv`或者`conda`，把依赖放入到一个文本文件中，执行如 `pip install -r requirements.txt`或者 `conda env create -f environment.yml`
这样的方式不能对开发环境，发布环境的依赖做出很好的区分：例如pytest这个包在发布到pypi上时候是不能依赖的，只对开发环境有意义（如果做就需要维护多份依赖配置文件).

`poetry`的依赖管理方式是在`pyproject.toml`文件中，添加依赖，例如：

```shell
poetry add pytest==6.0.0 --group test # 在测试环境所属分组添加依赖库
poetry use system # 使用你的终端中默认的python环境，例如conda 或者virtualenv的当前虚拟环境
poetry install --with test  # 安装test的依赖
```

**注意：执行poetry install 之前一定要使用`poetry use system`， 否则poetry 不会把依赖安装到你当前终端的virtual env里**

这样就会在pyproject.toml文件中测试环境添加依赖。当发布到pypi上时候，pytest不会被打入到发布包的依赖中。

具体poetry怎么管理多个环境的参考：[poetry依赖管理](https://python-poetry.org/docs/managing-dependencies/#dependency-groups)

### 2. 依赖安装

见上一节。

更详细的看[参考手册](https://python-poetry.org/docs/managing-dependencies/#dependency-groups)

**此处再次强调**，要在`conda`或者`virtuanenv`创建的虚拟环境里利用poetry安装依赖，必须在你的虚拟环境里先执行`poetry use system`，否则poetry会把依赖安装到poetry自己的虚拟环境里。

poetry其实也是一个虚拟环境管理软件，只不过此处我们就不再需要学个新东西了，其管理虚拟环境的命令为`poetry env `, 具体怎么用自己查手册，论成熟度目前确实无法和`virtuanenv`和`conda`比拟。其维护的虚拟环境的位置可以在[这里](https://python-poetry.org/docs/configuration/)找到。

### 3. 打包

```shell
poetry build
```

会在dist目录下生成源码包和whl包

如果要构造类似`pip install requests[socks5]`这种可选模块的包请参考 [这里](https://python-poetry.org/docs/pyproject/#extras)

### 4 发布到pypi

忽略， 由github Action结合tag机制自动完成。

## tox单元测试

一般发布一个python包需要在不同的python版本，例如python2.7, python3.x 进行单元测试，检测在不同操作系统windows, mac, linux上功能的一致性。

tox 只用敲一次命令即可帮助完成在不同pyton版本下的单元测试，结合github Action甚至可以完成在不同操作系统下的测试。

### 单元测试的编写

请自学吧，推荐pytest

### 本地运行单元测试

1. 测试文件命名规则：位于工程根目录的`tests`目录下，文件名以`test_`开头，例如`test_foo.py`，`test_bar.py`等等。
2. 本地测试命令： `tox`， 在指定的python 版本下测试 `tox -e py38`

## 参考

- 传送门[链接](https://stackoverflow.com/questions/59377071/how-can-i-get-tox-and-poetry-to-work-together-to-support-testing-multiple-versio)