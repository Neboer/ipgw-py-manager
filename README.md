# NEU ipgw manager
![](https://img.shields.io/badge/NEU-ipgw--manager-blue.svg)

<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="122" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="122" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h33v20H0z"/><path fill="#007ec6" d="M33 0h89v20H33z"/><path fill="url(#b)" d="M0 0h122v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="175" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="230">NEU</text><text x="175" y="140" transform="scale(.1)" textLength="230">NEU</text><text x="765" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="790">ipgw-manager</text><text x="765" y="140" transform="scale(.1)" textLength="790">ipgw-manager</text></g> </svg>


东北大学新版ipgw网关管理程序。

由于校内网关切换到统一认证，原有的用户名+密码登录网关的方式彻底失效。新版本的ipgw管理程序使用python编写，直接可以支持跨平台使用。

通过对学校ipgw的API提取解析后得到的纯粹的客户端，拥有高度的灵活性和定制性。

**程序尚未编写安装和设置读取模块，直接运行main.py并保证所有依赖项都在同一个目录下即可运行。**
## 用法
```
ipgw | ipgw -i | ipgw --login <username>
```
尝试使用设置中保存的cookie在当前ip登录网关。

如果cookie过期或失效需要重新认证，则会自动根据设置中保存的账号密码登录SSO，重新获取cookie并更新设置。
```
ipgw -o | ipgw --logout <uid>
```
登出当前账号上登录的任何设备（如果指定了uid编号，则登出指定的设备）
```
ipgw -c | ipgw --current
```
列出当前账号登录的所有ip、使用流量、使用时长，并指出当前登录的ip是否有其他账号登录。
```
ipgw -s | ipgw --status
```
尝试使用设置中保存的校园网网络管理后台账号密码登录网络中心后台，返回已用时长、套餐总额、剩余流量等信息。
```
ipgw --config
```
返回配置文件绝对路径。
