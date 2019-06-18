# NEU ipgw manager
![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

东北大学新版ipgw网关管理程序。

由于校内网关切换到统一认证，原有的用户名+密码登录网关的方式彻底失效。新版本的ipgw管理程序使用python编写，直接可以支持跨平台使用。

通过对学校ipgw的API提取解析后得到的纯粹的客户端，拥有高度的灵活性和定制性。

**程序尚未编写安装和设置读取模块，直接运行main.py并保证所有依赖项都在同一个目录下即可运行。**
## 用法
```
ipgw -i -u 201XXXXX | ipgw --login --username 201XXXXX
```
使用201XXXXX作为pass.neu.edu.cn的账号登录ipgw网关。程序会提示输入密码，输入后即可登录。

其中-i是login，-u是username，在不指定username时，程序会根据设置文件中保存的账号密码登录网关。
```
ipgw -o -u 201XXXXX
```
登出指定账号上登录的任何设备，其中，-o意为登出模式，如果没有指定username，则使用设置中默认的账号密码登出所有设备。
```
ipgw --logout <uid>
```
登出指定uid的设备。由于ipgw的特殊性，该操作并不需要登录账号。

uid是每个账号登录设备的一个特殊编号，在--login后，会返回一个设备列表。设备列表的最后一项就是uid，
只需要将其填入--logout后就可以实现下线了。
```
ipgw -c | ipgw --current
```
列出当前账号登录的所有ip、使用流量、使用时长，并指出当前登录的ip是否有其他账号登录。该行为并没有API支持，因此暂时没有实现。
```
ipgw -s | ipgw --status
```
尝试使用设置中保存的校园网网络管理后台账号密码登录网络中心后台，返回已用时长、套餐总额、剩余流量等信息。
这个功能需要解析网络中心数据的功能，相关模块还在编写中，暂时还不开放使用。
```
ipgw --config vim
```
使用vim打开配置文件。