import time
import json
import base64
import requests
from bs4 import BeautifulSoup

url = 'http://@/include/auth_action.php'

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Encoding": "gzip, deflate",
           "Accept-Language": "en-US,en;q=0.5",
           "Cache-Control": "max-age=0",
           "Connection": "keep-alive",
           "Host": "172.20.3.81:802",
           "Upgrade-Insecure-Requests": "1",
           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"
           }


def post(url, d):
    return requests.post(url=url, data=d, headers=headers)


def logout(username, password):
    r = requests.get('http://login.ecust.edu.cn', allow_redirects=False)
    yield f':: Requesting login.ecust.edu.cn...\n response as:\t{r}'
    if r.status_code != 302:
        redirect_url = BeautifulSoup(r.content, 'lxml').find('meta').get('content').split('url=')[-1]
        r = requests.get(redirect_url)
        r = r.history[0]
        yield f'(1/2) forced redirect:\t{redirect_url}'
    else:
        yield f'(1/2) performing redirect'
    ip = r.headers['Location'].split('//')[-1].split('/')[0]
    yield f'(2/2) target ip:\t{ip}'
    data = {"action": "logout", "username": username, "password": password, "ajax": "1"}
    yield f":: Processing logout...\n:: Sending post...\n\nresponse:\t{post(url.replace('@', ip), data).content.decode('utf-8')}\n"


def login(username, password, free=True):
    if free:
        username = f'{username}@free'
    yield f':: Encrypting password...'
    bs = base64.b64encode(password.encode("utf8"))
    password = '{B}'+str(bs).replace('b\'', '').replace('\'', '')
    yield f'(1/1) generate base64-utf8 password'
    r = requests.get('http://login.ecust.edu.cn', allow_redirects=False)
    yield f':: Requesting login.ecust.edu.cn...\n response as:\t{r}'
    if r.status_code != 302:
        redirect_url = BeautifulSoup(r.content, 'lxml').find('meta').get('content').split('url=')[-1]
        r = requests.get(redirect_url)
        r = r.history[0]
        yield f'(1/3) forced redirect:\t{redirect_url}'
    else:
        yield f'(1/3) performing redirect'
    ip = r.headers['Location'].split('//')[-1].split('/')[0]
    ac_id = r.headers['Location'].split('/index_')[-1].split('.')[0]
    yield f'(2/3) target ip:\t{ip}\n(3/3) get ac_id as:\t{ac_id}'
    data = {"action": "login", "username": username, "password": password, "ac_id": ac_id, "user_ip": "", "nas_ip": "", "user_mac": "", "ajax": "1"}
    yield f"\nresponse:\t{post(url.replace('@', ip), data).content.decode('utf-8')}\n"


def test_connection():
    try:
        test_url = 'http://www.baidu.com'
        print(f':: Test connection...\n:: Request from {test_url}...')
        r = requests.get(test_url, timeout=2)
        if "<html>\n<head>\n<meta http-equiv='refresh' content='1; url=http://www.baidu.com/&arubalp=" in r.text:
            print(' response: redirected')
            return False
        print(f' response:\t{r}')
        return True
    except Exception as e:
        print(e)
        print(f' response:\tconnection fail')
        return False


def scheduler(username, password, check_per_hour=1.5):
    while(True):
        with open('autologin.log', 'a') as f:
            x = f':: Awake at {time.ctime()}, check connection...'
            print(x)
            f.write(x)
            if not test_connection():
                for x in login(username, password):
                    print(x)
                    f.write(f'{x}\n')
            else:
                f.write(' ok\n')
        time.sleep(check_per_hour*60*60)


if __name__ == "__main__":

    # disconnect for test
    # for x in logout('your_username', 'your_password'):
    #     print(x)
    # time.sleep(5)

    scheduler('your_username', 'your_password')
