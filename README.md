# NEU ipgw manager

![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

![](./IPGW.svg)

东北大学ipgw网关管理程序重制版，仅支持统一身份认证用户名-密码登录

- 带有TUI(picotui)、GUI(tkinter)、CLI(argprase)三种操作模式，每种操作模式体验基本一致，可以在不同环境、不同平台上使用，操作非常方便。
- 格式化输出，输出内容为100%的中文，表格内容清晰易读，是对网页信息的高度简化。
- 兼容性极强，可以识别ipgw的所有状态和页面，比如停止服务、其他设备在线、费用不足等情况，并可以像网页端一样作出操作。
- 支持多用户管理，同时程序会记录用户最后一次登录的状态等，你可以在登录之后指定下线某个用户。你甚至可以从可以登录的用户中随机挑选用户登录。
- 配置文件可以很方便的修改，且位置唯一。
- 不仅仅是一个网络登录程序，内置core模块可以非常容易的重用，代替实现各种校内网页认证等功能，非常方便。

使用此脚本管理自己的ipgw连接，可以加快操作ipgw网关的速度，节省时间，无论是联网还是断网都十分方便。

本项目承诺长期更新，尽量做到功能稳定。目前已经有一个cli版本供使用，TUI和GUI版本正在开发中。

## 安装
### 自动安装
本项目支持自动安装，只需要执行

```pip install NEU-ipgw-manager```

项目基于Python 3.9开发，在3.8上通过了测试，除此之外不保证能够在其他版本Python环境中运行。

### 手动安装
由于有安装脚本的存在，整个安装过程非常简单。

首先克隆本仓库的源代码

`git clone https://github.com/Neboer/ipgw-py-manager.git`

然后执行`python setup.py install`

这样，就可以直接在命令行中执行`ipgw --help`来确认安装了。

## 快速上手

配置文件在安装之后自动存放在用户的home目录，可以在--help输出的信息中查看。详细的命令行用法参见下面的信息。

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

