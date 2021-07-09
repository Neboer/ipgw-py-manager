# 命令行参数说明

`ipgw action [options...]`

看如下几个实例（示例学号为20200001）：

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
登录默认账号，并下线其登陆的所有设备。

```shell
ipgw logout --sid 91260000
ipgw logout -i 91260000
```
下线指定sid的设备

```shell
ipgw logout -u 20200001 --sid 91260000
ipgw logout -u 20200001 -p thepassword -i 91260000
```
登录指定账号，下线指定sid的设备。当然，你也可以手动指定密码。

```shell
ipgw logout -u 20200001 -p thepassword
ipgw o -u 20200001 --only
ipgw o -u 20200001 --self
```

当不指定--sid的时候，程序会下线此账号登录的所有设备。
如果加--only选项，则只会留下自己登录；
如果加--self选项，则只会下线刚刚登录的自己（登录了个寂寞）

```shell
ipgw logout --last
ipgw o -l
```
当指定--last登出帐号时，程序会自动尝试登出上次登录而未登出的uid，使用上次登录这个uid时所用的帐号。

注意，所有指定sid的登出请求都会先进行一次不登录下线的尝试，如果尝试失败，则会识别用户提供的帐号进行登录。
### 账号管理

```shell
ipgw add 20200001 -p thepassword
```

与login行为基本相同，-p应该省略，由用户手动输入。

程序**不提供**删除账号、修改密码等对已保存账号进行操作的功能，有类似需求的时候请直接编辑配置文件。

### 全局设置

```shell
ipgw login 20200001 --silent
ipgw login 20200001 -s
```

`--silent`可以应用在任何场合，它阻止程序输出内容。使用silent选项之后，程序在成功登录网关之后不会打印任何信息。但是程序会在出错的时候打印错误信息。

```shell
ipgw login 20200001 --kick relogin
ipgw login 20200001 -k relogin
```

`--kick`可以覆盖设置中“当此ip地址已经有人在线”的处理方法，然后进行登录请求。
kick可以设为三种值：exit、logout和relogin。当请求遇到“此ip地址已经有人在线”时，exit会直接退出程序；logout则会将此人下线然后退出程序； relogin则是先将此人下线，然后再重新登录。

```shell
ipgw default 20200001
```

在添加用户之后，使用default命令将此用户设为默认登录用户。