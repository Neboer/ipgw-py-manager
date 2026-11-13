# NEU ipgw manager

[![PyPI](https://img.shields.io/pypi/v/NEU-ipgw-manager)](https://pypi.org/project/NEU-ipgw-manager/)

![](./IPGW.svg)

东北大学校园网网关（IPGW）的命令行工具，支持使用统一身份认证账号和密码登录，不需要打开浏览器。

- 登录、下线和查询网关状态；登录后以表格显示账号信息和在线设备。
- 保存多个账号并设置默认账号，适合在终端或无图形界面的设备上使用。
- `ipgw.core` 可在其他 Python 程序中复用。

## 版本记录

- 2021.11.02，东北大学校园网迎来了一次更新。此次更新修改了后端的api接口以及原有的登录策略和校验逻辑。
- 2021.11.03，NEU-ipgw-manager更新到了3.0版本，适配了这个新的api。
- 2024.09.13, NEU-ipgw-manager更新到了3.1版本，将整个软件的框架和构建系统升级到最新的Python标准中，并简化了安装要求。
- 2025.01.06, NEU-ipgw-manager更新到了3.2版本，规范了对应操作系统下配置文件生成的位置，更符合规范。
- 2026.03.08, NEU-ipgw-manager更新到了3.3版本，适配支持了教务处的新版SSO登录功能，感谢 [#13](https://github.com/Neboer/ipgw-py-manager/pull/13) 的贡献。
- 2026.11.13，[v3.4](https://github.com/Neboer/ipgw-py-manager/releases/tag/v3.4) 修复了统一身份认证登录脚本改名导致的登录失败，兼容 `login_neu_new.js` 和 `login_neu.js`（[#21](https://github.com/Neboer/ipgw-py-manager/pull/21)）；新增多平台独立可执行文件构建（[#19](https://github.com/Neboer/ipgw-py-manager/pull/19)）。

## 安装

### 从 PyPI 安装或升级

包声明的 Python 版本要求为 3.7 或更高。

```bash
python -m pip install --upgrade NEU-ipgw-manager
ipgw --version
```

### 下载独立可执行文件

无需安装 Python。进入 [v3.4 的 Build binaries 构建页面](https://github.com/Neboer/ipgw-py-manager/actions/runs/43393143945)，登录 GitHub 后，在 **Artifacts** 下载对应平台的压缩包：

| 平台 | 产物 |
| --- | --- |
| Linux x86_64 | `ipgw-linux-x86_64` |
| Windows x86_64 | `ipgw-windows-x86_64.exe` |
| macOS Intel | `ipgw-macos-x86_64` |
| macOS Apple Silicon | `ipgw-macos-arm64` |

`release-assets` 包含上述文件和 `SHA256SUMS`。这些文件是有保留期限的 Actions 产物，不是 GitHub Release 附件。

解压后，在 Linux 或 macOS 上可用 `chmod +x` 给对应文件添加执行权限，再运行该文件并传入 `--version`；在 Windows PowerShell 中运行 `.\ipgw-windows-x86_64.exe --version`。

### 从源码安装

```bash
git clone https://github.com/Neboer/ipgw-py-manager.git
cd ipgw-py-manager
python -m pip install .
ipgw --version
```

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
ipgw add -u 20200001
```

按提示输入密码。不要通过 `-p` 传递密码，以免留在 shell 历史记录中。

```shell
ipgw default -u 20200001
```

在添加用户之后，使用default命令将此用户设为默认登录用户。

程序**不提供**删除账号、修改密码等对已保存账号进行操作的功能，有类似需求的时候请直接编辑配置文件。

### 配置文件迁移

从 3.2 开始，`ipgw.json` 保存在系统的用户配置目录中。运行 `ipgw --help` 查看当前路径。如果账号仍保存在家目录下的旧配置文件中，可以用 `ipgw add -u <学工号>` 重新添加账号，再用 `ipgw default -u <学工号>` 设置默认账号。配置文件包含明文密码，请勿分享或提交到版本库。

### 详细输出

程序支持详细日志输出，如果程序出现异常，可以添加`-v`或者`--verbose`选项让程序输出更详细的日志，供debug使用。

### 系统代理设置

支持跳过系统代理进行登录，查询，登出。可以添加`--bypass-system-proxy`以跳过系统代理
