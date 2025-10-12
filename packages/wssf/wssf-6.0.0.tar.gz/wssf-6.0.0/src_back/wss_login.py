import base64
import concurrent.futures
import hashlib
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import base58
import requests
from Cryptodome.Cipher import DES
from Cryptodome.Util import Padding


def login_anonymous(session):
    r = session.post(
        url='https://www.wenshushu.cn/ap/login/anonymous',
        json={
            "dev_info": "{}"
        }
    )
    return r.json()['data']['token']


def download(url):
    try_login()
    
    def get_tid(token):
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/token',
            json={
                'token': token
            }
        )
        return r.json()['data']['tid']

    def mgrtask(tid):
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/mgrtask',
            json={
                'tid': tid,
                'password': ''
            }
        )
        rsp = r.json()
        expire = rsp['data']['expire']
        days, remainder = divmod(int(float(expire)), 3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f'文件过期时间:{days}天{hours}时{minutes}分{seconds}秒')

        file_size = rsp['data']['file_size']
        print(f'文件大小:{round(int(file_size)/1024**2,2)}MB')
        return rsp['data']['boxid'], rsp['data']['ufileid']  # pid

    def list_file(tid):
        bid, pid = mgrtask(tid)
        r = s.post(
            url='https://www.wenshushu.cn/ap/ufile/list',
            json={
                "start": 0,
                "sort": {
                    "name": "asc"
                },
                "bid": bid,
                "pid": pid,
                "type": 1,
                "options": {
                    "uploader": "true"
                },
                "size": 50
            }
        )
        rsp = r.json()
        filename = rsp['data']['fileList'][0]['fname']
        fid = rsp['data']['fileList'][0]['fid']
        print(f'文件名:{filename}')
        sign(bid, fid, filename)

    def down_handle(url, filename):
        print('开始下载!', end='\r')
        r = s.get(url, stream=True)
        dl_size = int(r.headers.get('Content-Length'))
        block_size = 2097152
        dl_count = 0
        with open(filename, 'wb') as f:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=block_size):
                f.write(chunk)
                dl_count += len(chunk)
                print(f'下载进度:{int(dl_count/dl_size*100)}%', end='\r')
            print('下载完成:100%')

    def sign(bid, fid, filename):
        r = s.post(
            url='https://www.wenshushu.cn/ap/dl/sign',
            json={
                'consumeCode': 0,
                'type': 1,
                'ufileid': fid
            }
        )
        if r.json()['data']['url'] == "" and \
                r.json()['data']['ttNeed'] != 0:
            print("对方的分享流量不足")
            sys.exit(0)
        url = r.json()['data']['url']
        down_handle(url, filename)

    if len(url.split('/')[-1]) == 16:
        token = url.split('/')[-1]
        tid = get_tid(token)
    elif len(url.split('/')[-1]) == 11:
        tid = url.split('/')[-1]

    list_file(tid)


def upload(filePath):
    try_login()
    
    chunk_size = 2097152
    file_size = os.path.getsize(filePath)
    ispart = True if file_size > chunk_size else False

    def read_file(block_size=chunk_size):
        partnu = 0
        with open(filePath, "rb") as f:
            while True:
                block = f.read(block_size)
                partnu += 1
                if block:
                    yield block, partnu
                else:
                    return

    def sha1_str(s):
        cm = hashlib.sha1(s.encode()).hexdigest()
        return cm

    def calc_file_hash(hashtype, block=None):
        read_size = chunk_size if ispart else None
        if not block:
            with open(filePath, 'rb') as f:
                block = f.read(read_size)
        if hashtype == "MD5":
            hash_code = hashlib.md5(block).hexdigest()
        elif hashtype == "SHA1":
            hash_code = hashlib.sha1(block).hexdigest()
        return hash_code

    def get_epochtime():
        r = s.get(
            url='https://www.wenshushu.cn/ag/time',
            headers={
                "Prod": "com.wenshushu.web.pc",
                "Referer": "https://www.wenshushu.cn/"
            }
        )
        rsp = r.json()
        return rsp["data"]["time"]  # epochtime expires in 60s

    def get_cipherheader(epochtime, token, data):
        # cipherMethod: DES/CBC/PKCS7Padding
        json_dumps = json.dumps(data, ensure_ascii=False)
        md5_hash_code = hashlib.md5((json_dumps+token).encode()).hexdigest()
        base58_hash_code = base58.b58encode(md5_hash_code)
        key_iv = (
            # 时间戳逆序取5位并作为时间戳字串索引再次取值，最后拼接"000"
            "".join([epochtime[int(i)] for i in epochtime[::-1][:5]]) + "000"
        ).encode()
        cipher = DES.new(key_iv, DES.MODE_CBC, key_iv)
        cipherText = cipher.encrypt(
            Padding.pad(base58_hash_code, DES.block_size, style="pkcs7")
        )
        return base64.b64encode(cipherText)

    def storage():
        r = s.post(
            url='https://www.wenshushu.cn/ap/user/storage',
            json={}
        )
        rsp = r.json()
        rest_space = int(rsp['data']['rest_space'])
        send_space = int(rsp['data']['send_space'])
        storage_space = rest_space + send_space
        print('当前已用空间:{}GB,剩余空间:{}GB,总空间:{}GB'.format(
            round(send_space / 1024**3, 2),
            round(rest_space / 1024**3, 2),
            round(storage_space / 1024**3, 2)
        ))

    def userinfo():
        s.post(
            url='https://www.wenshushu.cn/ap/user/userinfo',
            json={"plat": "pcweb"}
        )

    def addsend():
        userinfo()
        storage()
        epochtime = get_epochtime()
        req_data = {
            "sender": "",
            "remark": "",
            "isextension": False,
            "notSaveTo": False,
            "notDownload": False,
            "notPreview": False,
            "downPreCountLimit": 0,
            "trafficStatus": 0,
            "pwd": "",
            "expire": "1",
            "recvs": [
                "social",
                "public"
            ],
            "file_size": file_size,
            "file_count": 1
        }
        # POST的内容在服务端会以字串形式接受然后直接拼接X-TOKEN，不会先反序列化JSON字串再拼接
        # 加密函数中的JSON序列化与此处的JSON序列化的字串形式两者必须完全一致，否则校验失败
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/addsend',
            json=req_data,
            headers={
                "A-code": get_cipherheader(epochtime, s.headers['X-TOKEN'], req_data),
                "Prod": "com.wenshushu.web.pc",
                "Referer": "https://www.wenshushu.cn/",
                "Origin": "https://www.wenshushu.cn",
                "Req-Time": epochtime,
            }
        )
        rsp = r.json()
        if rsp["code"] == 1021:
            print(f'操作太快啦！请{rsp["message"]}秒后重试')
            sys.exit(0)
        data = rsp["data"]
        assert data, "需要滑动验证码"
        bid, ufileid, tid = data["bid"], data["ufileid"], data["tid"]
        upId = get_up_id(bid, ufileid, tid, file_size)
        return bid, ufileid, tid, upId

    def get_up_id(bid: str, ufileid: str, tid: str, file_size: int):
        r = s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/getupid",
            json={
                "preid": ufileid,
                "boxid": bid,
                "linkid": tid,
                "utype": "sendcopy",
                "originUpid": "",
                "length": file_size,
                "count": 1
            }
        )
        return r.json()["data"]["upId"]

    def psurl(fname, upId, file_size, partnu=None):
        payload = {
            "ispart": ispart,
            "fname": fname,
            "fsize": file_size,
            "upId": upId,
        }
        if ispart:
            payload["partnu"] = partnu
        r = s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/psurl",
            json=payload
        )
        rsp = r.json()
        url = rsp["data"]["url"]  # url expires in 600s (10 minutes)
        return url

    def copysend(boxid, taskid, preid):
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/copysend',
            json={
                'bid': boxid,
                'tid': taskid,
                'ufileid': preid
            }
        )
        rsp = r.json()
        print(f"个人管理链接：{rsp['data']['mgr_url']}")
        print(f"公共链接：{rsp['data']['public_url']}")

    def fast():
        boxid, preid, taskid, upId = addsend()
        cm1, cs1 = calc_file_hash("MD5"), calc_file_hash("SHA1")
        cm = sha1_str(cm1)
        name = os.path.basename(filePath)

        payload = {
            "hash": {
                "cm1": cm1,  # MD5
                "cs1": cs1,  # SHA1
            },
            "uf": {
                "name": name,
                "boxid": boxid,
                "preid": preid
            },
            "upId": upId
        }

        if not ispart:
            payload['hash']['cm'] = cm  # 把MD5用SHA1加密
        for _ in range(2):
            r = s.post(
                url='https://www.wenshushu.cn/ap/uploadv2/fast',
                json=payload
            )
            rsp = r.json()
            can_fast = rsp["data"]["status"]
            ufile = rsp['data']['ufile']
            if can_fast and not ufile:
                hash_codes = ''
                for block, _ in read_file():
                    hash_codes += calc_file_hash("MD5", block)
                payload['hash']['cm'] = sha1_str(hash_codes)
            elif can_fast and ufile:
                print(f'文件{name}可以被秒传！')
                getprocess(upId)
                copysend(boxid, taskid, preid)
                sys.exit(0)

        return name, taskid, boxid, preid, upId

    def getprocess(upId: str):
        while True:
            r = s.post(
                url="https://www.wenshushu.cn/ap/ufile/getprocess",
                json={
                    "processId": upId
                }
            )
            if r.json()["data"]["rst"] == "success":
                return True
            time.sleep(1)

    def complete(fname, upId, tid, boxid, preid):
        s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/complete",
            json={
                "ispart": ispart,
                "fname": fname,
                "upId": upId,
                "location": {
                    "boxid": boxid,
                    "preid": preid
                }
            }
        )
        copysend(boxid, tid, preid)

    def file_put(psurl_args, fn, offset=0, read_size=chunk_size):
        with open(fn, "rb") as fio:
            fio.seek(offset)
            requests.put(url=psurl(*psurl_args), data=fio.read(read_size))

    def upload_main():
        fname, tid, boxid, preid, upId = fast()
        if ispart:
            print('文件正在被分块上传！')
            with ThreadPoolExecutor(max_workers=4) as executor:  # or use os.cpu_count()
                future_list = []
                for i in range((file_size + chunk_size - 1)//chunk_size):
                    ul_size = chunk_size if chunk_size*(i+1) <= file_size \
                        else file_size % chunk_size
                    future_list.append(executor.submit(
                        file_put, [fname, upId, ul_size, i+1],
                        filePath, chunk_size*i, ul_size
                    ))
                future_length = len(future_list)
                count = 0
                for _ in concurrent.futures.as_completed(future_list):
                    count += 1
                    sp = count / future_length * 100
                    print(f'分块进度:{int(sp)}%', end='\r')
                    if sp == 100:
                        print('上传完成:100%')
        else:
            print('文件被整块上传！')
            file_put([fname, upId, file_size], filePath, 0, file_size)
            print('上传完成:100%')

        complete(fname, upId, tid, boxid, preid)
        getprocess(upId)
    upload_main()

def display_login_instructions():
    instructions = """获取X-TOKEN以便登录你自己的账号：
1. 打开浏览器，访问 https://www.wenshushu.cn
2. 登录你的账号
3. 按F12打开开发者工具
4. 切换到Network(网络)标签
5. 刷新页面或进行任意操作
6. 找到任意一个请求（例如/ap/user/userinfo）
7. 查看Request Headers，找到最下方的X-TOKEN字段
8. 复制X-TOKEN字段（大概率为27位，30B开头的字符串）
9. 使用`python wss.py login "30Bxxxxxxxxxxxxxxxxxxxxxxxx"`登录
"""
    print(instructions)

def write_token(token):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, 'token.txt'), 'w') as f:
        f.write(token)

    print(f"尝试使用 X-TOKEN: {token} 登录")
    s.headers['X-TOKEN'] = token
    test_userinfo()
    test_storage()

def test_userinfo():
    r = s.post(
        url='https://www.wenshushu.cn/ap/user/userinfo',
        json={"plat": "pcweb"}
    )
    if r.json()["code"] != 0:
        print(f"登录失败，错误: {r.json()}")
        return
    user_data = r.json()['data']
    print(f"登录成功")
    if user_data['name'] != "":
        print(f"用户名: {user_data['name']}")
    if user_data['email'] != "":
        print(f"邮箱: {user_data['email']}")
    if user_data['tel'] != "":
        print(f"手机号: {user_data['tel']}")

def test_storage():
    r = s.post(
        url='https://www.wenshushu.cn/ap/user/storage',
        json={}
    )
    if r.json()["code"] != 0:
        print(f"登录失败，错误: {r.json()}")
        return
    storage_data = r.json()['data']
    used = int(storage_data['send_space'])
    rest = int(storage_data['rest_space'])
    total = used + rest
    print(f"当前已用空间: {round(used / 1024**3, 2)}GB")
    print(f"剩余空间: {round(rest / 1024**3, 2)}GB")
    print(f"总空间: {round(total / 1024**3, 2)}GB")
    
def try_login():
    # try to login with token.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, 'token.txt')):
        with open(os.path.join(script_dir, 'token.txt'), 'r') as f:
            token = f.read()
        print(f"尝试使用已保存的 X-TOKEN: {token} 登录")
        s.headers['X-TOKEN'] = token
        test_userinfo()
        test_storage()
        print()
    else:
        print("未找到 token.txt，使用匿名登录")
        s.headers['X-TOKEN'] = login_anonymous(s)

if __name__ == "__main__":
    s = requests.Session()
    # s.headers['X-TOKEN'] = login_anonymous(s)
    s.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"
    s.headers['Accept-Language'] = "en-US, en;q=0.9"  # NOTE: require header, otherwise return {"code":-1, ...}
    try:
        command = sys.argv[1]
        if command.lower() in ['upload', 'u']:
            file = sys.argv[2]
            upload(file)
        elif command.lower() in ['download', 'd']:
            url = sys.argv[2]
            download(url)
        elif command.lower() in ['login', 'l']:
            if len(sys.argv) <= 2:
                display_login_instructions()
            else:
                token = sys.argv[2]
                write_token(token)
    except IndexError:
        print('请输入正确命令\n',
              '上传:[python wss.py upload "file.exe"]\n',
              '下载:[python wss.py download "url"]\n',
              '登录:[python wss.py login "X-TOKEN"]')
    except Exception as e:
        traceback.print_exc()
