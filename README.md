# NEU ipgw manager
![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

东北大学新版ipgw网关管理程序。

由于校内网关切换到统一认证，原有的用户名+密码登录网关的方式彻底失效。新版本的ipgw管理程序使用python编写，直接可以支持跨平台使用。

通过对学校ipgw的API提取解析后得到的纯粹的客户端，拥有高度的灵活性和定制性。

**未来会考虑直接适配python图形界面**
## 用法
```
ipgw | ipgw -i | ipgw --login
```
尝试使用设置中保存的cookie在当前ip登录网关。

如果cookie过期或失效需要重新认证，则会自动根据设置中保存的账号密码登录SSO，重新获取cookie并更新设置。
```
ipgw -o | ipgw --logout[=id]
```
登出当前ip上登录的任何账号（如果指定了ip编号，则登出指定的设备）并打印登出的列表。
```
ipgw -l | ipgw --list
```
列出当前账号登录的所有ip、使用流量、使用时长，并指出当前登录的ip是否有其他账号登录。
```
ipgw -s | ipgw --status
```
尝试使用设置中保存的校园网网络管理后台账号密码登录网络中心后台，返回已用时长、套餐总额、剩余流量等信息。
```
ipgw --set
```
使用文本编辑器打开配置文件，可以直接修改并保存。