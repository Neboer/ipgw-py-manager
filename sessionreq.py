import requests
from bs4 import BeautifulSoup, Tag


def pass_authenticate(username, password, session: requests.Session):
    r = session.get('http://ipgw.neu.edu.cn/srun_cas.php?ac_id=1')
    soup = BeautifulSoup(r.text, 'html.parser')
    form: Tag = soup.find("form", {'id': 'loginForm'})
    destination = form.attrs['action']
    ext_lt_string = form.find("input", {'id': 'lt'}).attrs["value"]
    formData = {
        'rsa': username + password + ext_lt_string,
        'ul': len(username),
        'pl': len(password),
        'lt': ext_lt_string,
        'execution': 'e5s1',
        '_eventId': 'submit'
    }
    print(destination)


connect_session = requests.Session()
connect_session.get('http://ipgw.neu.edu.cn/srun_portal_pc.php?ac_id=1&')
pass_authenticate('20183345', 'dddsddfs', connect_session)

# with open("out.html",'w') as file:
#     file.write(r.text)
