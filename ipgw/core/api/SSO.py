import logging
from urllib.parse import parse_qs, urlparse
from requests import Session, codes
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
from .SSO_error import BackendError, UnionAuthError, UnknownPageError

ua = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'''
# target = '''https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_cas.php%3Fac_id%3D1'''
target = '''https://pass.neu.edu.cn/tpass/login?service=http%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_portal_sso%3Fac_id%3D1'''


class PageTitle:
    UnionAuth = "智慧东大--统一身份认证"
    SystemHint = "系统提示"
    EmailVerification = "智慧东大"  # 出现这个标题意味着用户需要进行邮箱认证
    IPGWControlGateway = "IP控制网关"


class SSOPage(TypedDict):
    form_lt_string: str
    form_execution: str
    form_destination: str


# 准备一个SSO内容，里面有
def SSO_prepare(session: Session) -> SSOPage:
    page_soup = BeautifulSoup(session.get(target).text, 'lxml')
    form: Tag = page_soup.find("form", {'id': 'loginForm'})
    return {
        "form_lt_string": form.find("input", {'id': 'lt'}).attrs["value"],
        "form_destination": form.attrs['action'],
        "form_execution": form.find("input", {'name': 'execution'}).attrs["value"]
    }


# 请求SSO和认证SSO两个操作合并到一个API接口中，直接操作。返回一个SSO ticket。这个函数会触发异常
def SSO_login(session: Session, page: SSOPage, username, password, ac_id) -> str:
    form_data = {
        'rsa': username + password + page['form_lt_string'],
        'ul': len(username),
        'pl': len(password),
        'lt': page['form_lt_string'],
        'execution': page['form_execution'],
        '_eventId': 'submit'
    }
    login_first_result = session.post("https://pass.neu.edu.cn" + page['form_destination'], data=form_data, allow_redirects=True)  # 允许跳转
    login_first_result_soup = BeautifulSoup(login_first_result.text, "lxml")
    title_soup = login_first_result_soup.find("title")
    if not title_soup:
        # 问题出现！ 这个问题可能是后端返回了一个redis错误的页面
        raise BackendError(login_first_result_soup.text)
    else:
        response_page_title = title_soup.text
        if response_page_title == PageTitle.IPGWControlGateway:
            # 登录成功！
            return parse_qs(urlparse(login_first_result.url).query)['ticket'][0]
        elif response_page_title == PageTitle.UnionAuth:
            # 用户名或密码错误
            raise UnionAuthError()
        elif response_page_title == PageTitle.EmailVerification:
            # 这个页面可能会出现，因为目标未绑定邮箱。我们这里的处理方法就是简单跳过。
            logging.warning("帐号未绑定邮箱")
            login_skip_email_result = session.get(
                f"https://pass.neu.edu.cn/tpass/login?service=http%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_portal_sso%3Fac_id%3D{ac_id}", allow_redirects=True)
            return parse_qs(urlparse(login_skip_email_result.url).query)['ticket'][0]
        else:
            raise UnknownPageError(login_first_result_soup)

    # print(ticket)
    # session.get(login_first_result.next.url)
    # session.get(f"http://ipgw.neu.edu.cn/srun_portal_sso?ac_id=1&ticket={ticket}")
    # login_final_result = session.get(f'http://ipgw.neu.edu.cn/v1/srun_portal_sso?ac_id=1&ticket={ticket}', headers={
    #     "referer": f"http://ipgw.neu.edu.cn/srun_portal_sso?ac_id=1&ticket={ticket}"})
    # print(login_final_result.text)
