# NEU ipgw manager

![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

![](./IPGW.svg)

东北大学ipgw网关管理程序重制版，仅支持统一身份认证用户名-密码登录

- 带有TUI(picotui)、GUI(tkinter)、CLI(argprase)三种操作模式，每种操作模式体验基本一致，可以在不同环境、不同平台上使用，操作非常方便。
- 格式化输出，输出内容为100%的中文，表格内容清晰易读，是对网页信息的高度简化。
- 兼容性极强，可以识别ipgw的所有状态和页面，比如停止服务、其他设备在线、费用不足等情况，并可以像网页端一样作出操作。
- 支持多用户管理，同时程序会记录用户最后一次登录的状态等，你可以在登录之后指定下线某个用户。你甚至可以从可以登录的用户中随机挑选用户登录。
- 配置文件可以很方便的修改，且位置唯一。

使用此脚本管理自己的ipgw连接，可以加快操作ipgw网关的速度，节省时间，无论是联网还是断网都十分方便。

本项目承诺长期更新，尽量做到功能稳定。目前已经有一个cli版本供使用，TUI和GUI版本正在开发中。

## 安装与部署

手动安装ipgw-py-manager的方法有些复杂，因为是python脚本。ipgw-py-manager计划在下一个版本发布到pip软件源中，这样安装就会变得非常简单了。

### 1. 安装Python

首先，为了运行本程序，你需要一个Python环境。如果你已经有Python环境了，那么Python版本不能低于3.7。程序在设计的时候没有考虑低版本兼容性， 因此请使用尽量高的Python版本运行本程序，确保不会出现问题。

### 2. 安装依赖

其次，你需要安装requirements.txt中的所有包，执行`pip install -r requirements.txt`。

然后，你需要安装`lxml`。lxml用来辅助`beautifulsoup`做HTML文档解析，速度比较快。lxml在Windows上安装只需要执行如下命令：
`pip install lxml`即可；如果你的操作系统是Linux发行版，那么请参照 [lxml官网](https://lxml.de/installation.html) 上的内容进行安装。

### 3. 添加配置文件

在项目的根目录下，有一个配置文件default_config.json。编辑这个文件的username和password为你自己账号的用户名和密码，同时你也可以多添加几个已知帐号的用户。
然后把这个文件拷贝到`C:\Users\<你的用户名>\ipgw.json`。注意文件名要改动一下。

这个过程也可以通过执行`install_config.py`快速执行。

### 4. 添加环境变量

现在，`bin/ipgw.ps1`可以执行了。为了更方便的执行代码，你可以把bin文件夹添加进PATH环境变量中。

### 5. 完成！

恭喜，ipgw程序已经成功安装进你的电脑，现在你要做的就是重新打开一个命令行窗口，然后执行`ipgw --help`，看到输出的帮助信息，便成功了。

## 使用

本程序目前只支持命令行使用，具体使用方法请参见[cli用法文档](./cli/README.md)