# NEU ipgw manager

![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

![](./IPGW.svg)

东北大学ipgw网关管理程序重制版，仅支持统一身份认证用户名-密码登录

- 漂亮的、格式化的表格输出，内容清晰易读，和网页端提供相同的信息。
- 兼容强，可以识别ipgw的所有状态和页面，比如停止服务、其他设备在线、费用不足等情况，并可以像网页端一样作出操作。
- 适配广泛，对于无线网络、有线网络、安卓/IOS/Windows设备都有很好的支持，你完全可以把它作为无界面服务器联网的工具，同时比浏览器使用方便很多。
- 支持多用户管理，带有配置文件，可以用简单的命令执行复杂的操作。当然也可以覆盖默认的行为。配置文件人类可读，修改起来很方便。
- 模拟真实浏览器操作，稳定运行多年，无任何使用风险。
- 不仅仅是一个网络登录程序，内置core模块可以非常容易的重用，代替实现各种校内网页认证等功能，非常方便。

使用此脚本管理自己的ipgw连接，可以加快操作ipgw网关的速度，节省时间，无论是联网还是断网都十分方便。

本项目承诺长期更新，长期可用，功能稳定。

- 2021.11.02，东北大学校园网迎来了一次更新。此次更新修改了后端的api接口以及原有的登录策略和校验逻辑。
- 2021.11.03，NEU-ipgw-manager更新到了3.0版本，适配了这个新的api。
- 2024.09.13, NEU-ipgw-manager更新到了3.1版本，将整个软件的框架和构建系统升级到最新的Python标准中，并简化了安装要求。
- 2025.01.06, NEU-ipgw-manager更新到了3.2版本，规范了对应操作系统下配置文件生成的位置，更符合规范。

## 安装
### 自动安装
本软件已经发布到PyPI，只需要执行

```pip install NEU-ipgw-manager```

本项目支持从3.7开始的所有现代Python版本，项目本身是在Python 3.12上开发的。

### 手动安装
首先克隆本仓库的源代码

`git clone https://github.com/Neboer/ipgw-py-manager.git`

切换到文件夹中，`cd ipgw-py-manager`

然后执行`pip install .`从源代码安装本软件

这样，就可以直接在命令行中执行`ipgw --version`来确认安装了。

## 快速上手

配置文件将在首次使用后，存放在系统的配置路径，可以在 `--help` 输出的信息中查看。详细的命令行用法参见下面的信息。

对于首次安装的用户，你需要添加一个用户并设置其为默认用户，操作方法如下：

```shell
ipgw add -u 20180001
```

输入密码，成功添加用户。

```shell
ipgw default -u 20180001
```

成功设置用户为默认用户。

之后，登录网关：

```shell
ipgw i
```

如果用户名和密码没有问题，此时应该显示登录成功，并报告登录的结果。

登出：

```shell
ipgw o
```

快速登出当前登录的帐号。

## 命令行参数说明

`ipgw action [options...]`

看如下几个实例（示例学号为20200001）：

### 状态

```shell
ipgw status
ipgw s
```

获取当前ipgw网络连接状态。

### 登录

```shell
ipgw login
ipgw i
```

使用已保存的默认用户名密码登录并联网。在任何时候login都可以替换成i。

---

```shell
ipgw login -u 20200001
ipgw login --username 20200001
```

登录20200001，程序会在已保存的账号中寻找20200001的密码，如果找不到则会要求用户输入密码。

---

```shell
ipgw login -u 20200001 --password thepassword
ipgw login -u 20200001 -p thepassword
```

使用指定密码登录账号，不推荐此类方法，建议不要在命令行中直接输入密码。

登录之后，程序会显示账号信息列表和已登录设备列表。

### 登出

```shell
ipgw logout
ipgw o
```

登出本机。

---

```shell
ipgw logout --all
ipgw o --all
```

下线所有设备。

### 账号管理

```shell
ipgw add 20200001 -p thepassword
```

与login行为基本相同，-p应该省略，由用户手动输入。

```shell
ipgw default -u 20200001
```

在添加用户之后，使用default命令将此用户设为默认登录用户。

程序**不提供**删除账号、修改密码等对已保存账号进行操作的功能，有类似需求的时候请直接编辑配置文件。

### 配置文件迁移

更新到3.2版本以上时，程序的配置文件路径发生改变，如果您在家目录下有 `ipgw.json` 文件，更新完本软件之后，请执行 `ipgw login` 以登录， 

### 详细输出

程序支持详细日志输出，如果程序出现异常，可以添加`-v`或者`--verbose`选项让程序输出更详细的日志，供debug使用。

### 系统代理设置

支持跳过系统代理进行登录，查询，登出。可以添加`--bypass-system-proxy`以跳过系统代理
