import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
import signal
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import base58
import requests
from Cryptodome.Cipher import DES
from Cryptodome.Util import Padding


# 全局变量用于控制上传中断
upload_interrupted = False
interrupt_count = 0
current_operation = None  # 'upload' 或 'download'
resume_enabled = False    # 是否启用了断点续传

def signal_handler(signum, frame):
    """处理Ctrl+C中断信号"""
    global upload_interrupted, interrupt_count, current_operation, resume_enabled
    interrupt_count += 1
    
    if interrupt_count == 1:
        upload_interrupted = True
        # 根据当前操作显示相应的中断消息
        if current_operation == 'download':
            print(f"\n{_('download_interrupted')}")
        else:
            print(f"\n{_('upload_interrupted')}")
        
        # 只在启用断点续传时显示保存信息
        if resume_enabled:
            print(_('saving_resume_info'))
        # 第一次Ctrl+C，优雅退出
    elif interrupt_count >= 2:
        # 第二次Ctrl+C，强制退出
        print(f"\n{_('force_exit')}")
        import os
        os._exit(1)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

# 断点续传信息存储

# 语言系统
LANG = 'zh'  # 默认语言

TRANSLATIONS = {
    'zh': {
        'file_expires': '文件过期时间:{}天{}时{}分{}秒',
        'file_size': '文件大小:{} MB',
        'file_name': '文件名:{}',
        'detected_resume_with_progress': '检测到断点续传，已下载: {} ({}%)',
        'detected_resume': '检测到断点续传，已下载: {}',
        'starting_download': '开始下载!',
        'download_complete': '下载完成!',
        'download_error': '下载出错: {}',
        'download_cancelled': '下载已取消，断点续传信息已保存',
        'download_cancelled_no_resume': '下载已取消',
        'download_interrupted': '检测到中断信号，正在停止下载...',
        'resume_info_saved': '已保存断点续传信息，下次可使用 -c 参数继续下载',
        'share_traffic_insufficient': '对方的分享流量不足',
        'used_space': '当前已用空间:{}GB,剩余空间:{}GB,总空间:{}GB',
        'too_fast': '操作太快啦！请{}秒后重试',
        'need_verification': '需要滑动验证码',
        'personal_link': '个人管理链接：{}',
        'public_link': '公共链接：{}',
        'instant_transfer': '文件{}可以被秒传！',
        'file_chunked_upload': '文件正在被分块上传！',
        'upload_complete': '上传完成!',
        'upload_error': '上传出错: {}',
        'file_single_upload': '文件被整块上传！',
        'upload_complete_100': '上传完成:100%',
        'upload_interrupted': '检测到中断信号，正在停止上传...',
        'saving_resume_info': '正在保存断点续传信息...',
        'upload_cancelled': '上传已取消',
        'force_exit': '强制退出程序...',
        'days': '天',
        'hours': '时',
        'minutes': '分',
        'seconds': '秒'
    },
    'en': {
        'file_expires': 'File expires in: {} days {} hours {} minutes {} seconds',
        'file_size': 'File size: {} MB',
        'file_name': 'File name: {}',
        'detected_resume_with_progress': 'Detected resume, downloaded: {} ({}%)',
        'detected_resume': 'Detected resume, downloaded: {}',
        'starting_download': 'Starting download!',
        'download_complete': 'Download complete!',
        'download_error': 'Download error: {}',
        'download_cancelled': 'Download interrupted, saving resume info...',
        'download_cancelled_no_resume': 'Download cancelled',
        'download_interrupted': 'Download interrupted, stopping download...',
        'resume_info_saved': 'Resume info saved, you can continue with -c parameter',
        'share_traffic_insufficient': 'Share traffic insufficient',
        'used_space': 'Current used space: {} GB, remaining space: {} GB, total space: {} GB',
        'too_fast': 'Too fast! Please try again after {} seconds',
        'need_verification': 'Need to slide verification code',
        'personal_link': 'Personal management link: {}',
        'public_link': 'Public link: {}',
        'instant_transfer': 'File {} can be transferred instantly!',
        'file_chunked_upload': 'File is being chunked up!',
        'upload_complete': 'Upload complete!',
        'upload_error': 'Upload error: {}',
        'file_single_upload': 'File is being uploaded in one go!',
        'upload_complete_100': 'Upload complete: 100%',
        'upload_interrupted': 'Upload interrupted, saving resume info...',
        'saving_resume_info': 'Saving resume info...',
        'upload_cancelled': 'Upload cancelled',
        'force_exit': 'Force exit program...',
        'days': 'days',
        'hours': 'hours', 
        'minutes': 'minutes',
        'seconds': 'seconds'
    }
}

def _(key, *args):
    """翻译函数"""
    global LANG
    text = TRANSLATIONS.get(LANG, TRANSLATIONS['zh']).get(key, key)
    if args:
        return text.format(*args)
    return text

def format_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:  # 字节
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"

def format_speed(bytes_per_second):
    """格式化速度显示"""
    return f"{format_size(bytes_per_second)}/s"

def draw_progress_bar(current, total, width=30, start_time=None):
    """绘制进度条"""
    if total == 0:
        return "0.0% [" + " " * width + "] 0 B/0 B 0 B/s"
    
    # 计算百分比
    percentage = min(100.0, (current / total) * 100)
    
    # 计算进度条填充
    filled_width = int(width * current // total)
    bar = "█" * filled_width + "░" * (width - filled_width)
    
    # 计算速度
    speed_str = ""
    if start_time is not None:
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = current / elapsed_time
            speed_str = f" {format_speed(speed)}"
    
    # 格式化大小
    current_str = format_size(current)
    total_str = format_size(total)
    
    return f"{percentage:5.1f}% [{bar}] {current_str}/{total_str}{speed_str}"

def save_resume_info(filename, info):
    """保存断点续传信息"""
    resume_file = f"{filename}.resume"
    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(info, f)

def load_resume_info(filename):
    """加载断点续传信息"""
    resume_file = f"{filename}.resume"
    if os.path.exists(resume_file):
        try:
            with open(resume_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def remove_resume_info(filename):
    """删除断点续传信息"""
    resume_file = f"{filename}.resume"
    if os.path.exists(resume_file):
        os.remove(resume_file)

def get_file_size(filename):
    """获取已下载文件大小"""
    if os.path.exists(filename):
        return os.path.getsize(filename)
    return 0


def login_anonymous(session):
    r = session.post(
        url='https://www.wenshushu.cn/ap/login/anonymous',
        json={
            "dev_info": "{}"
        }
    )
    return r.json()['data']['token']


def download(url, enable_resume=False):
    global LANG
    def get_tid(token):
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/token',
            json={
                'token': token
            }
        )
        return r.json()['data']['tid']

    def mgrtask(tid):
        global LANG
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
        print(_('file_expires', days, hours, minutes, seconds))

        file_size = rsp['data']['file_size']
        print(_('file_size', round(int(file_size)/1024**2,2)))
        return rsp['data']['boxid'], rsp['data']['ufileid']  # pid

    def list_file(tid):
        global LANG
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
        print(_('file_name', filename))
        sign(bid, fid, filename)

    def down_handle(url, filename):
        global LANG
        # 检查断点续传
        downloaded_size = 0
        mode = 'wb'
        headers = {}
        
        if enable_resume:
            resume_info = load_resume_info(filename)
            if resume_info and os.path.exists(filename):
                downloaded_size = get_file_size(filename)
                if downloaded_size > 0:
                    headers['Range'] = f'bytes={downloaded_size}-'
                    mode = 'ab'
                    # 计算已下载百分比
                    if 'total_size' in resume_info and resume_info['total_size'] > 0:
                        progress = (downloaded_size / resume_info['total_size']) * 100
                        print(_('detected_resume_with_progress', format_size(downloaded_size), f'{progress:.1f}'))
                    else:
                        print(_('detected_resume', format_size(downloaded_size)))
        
        print(_('starting_download'), end='\r')
        r = s.get(url, stream=True, headers=headers)
        
        # 检查服务器是否支持断点续传
        if 'Content-Range' in r.headers:
            total_size = int(r.headers['Content-Range'].split('/')[-1])
        else:
            total_size = int(r.headers.get('Content-Length', 0)) + downloaded_size
            
        # 保存断点续传信息
        if enable_resume:
            resume_info = {
                'url': url,
                'filename': filename,
                'total_size': total_size,
                'downloaded_size': downloaded_size
            }
            save_resume_info(filename, resume_info)
        
        block_size = 2097152
        dl_count = downloaded_size
        start_time = time.time()
        last_update_time = start_time
        
        try:
            with open(filename, mode) as f:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=block_size):
                    # 检查是否被中断
                    if upload_interrupted:
                        print()  # 换行
                        # 根据是否启用断点续传显示不同的消息
                        if enable_resume:
                            print(_('download_cancelled'))
                            # 更新断点续传信息
                            resume_info['downloaded_size'] = dl_count
                            save_resume_info(filename, resume_info)
                        else:
                            print(_('download_cancelled_no_resume'))
                        return
                        
                    f.write(chunk)
                    dl_count += len(chunk)
                    
                    # 更新进度条（限制更新频率，避免闪烁）
                    current_time = time.time()
                    if current_time - last_update_time >= 0.1:  # 每100ms更新一次
                        progress_bar = draw_progress_bar(dl_count, total_size, start_time=start_time)
                        print(f'\r{progress_bar}', end='', flush=True)
                        last_update_time = current_time
                
                # 最终进度显示
                if not upload_interrupted:
                    progress_bar = draw_progress_bar(total_size, total_size, start_time=start_time)
                    print(f'\r{progress_bar}')
                    print(_('download_complete'))
                
                # 下载完成，删除断点续传信息
                if enable_resume and not upload_interrupted:
                    remove_resume_info(filename)
                    
        except KeyboardInterrupt:
            print()  # 换行
            # 根据是否启用断点续传显示不同的消息
            if enable_resume:
                print(_('download_cancelled'))
                # 更新断点续传信息
                resume_info['downloaded_size'] = dl_count
                save_resume_info(filename, resume_info)
                print(_('resume_info_saved'))
            else:
                print(_('download_cancelled_no_resume'))
            return
        except Exception as e:
            print(_('download_error', e))
            if enable_resume:
                # 更新断点续传信息
                resume_info['downloaded_size'] = dl_count
                save_resume_info(filename, resume_info)
                print(_('resume_info_saved'))
            raise

    def sign(bid, fid, filename):
        global LANG
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
            print(_('share_traffic_insufficient'))
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
    global LANG
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
        global LANG
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
        global LANG
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
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/user/storage',
            json={}
        )
        rsp = r.json()
        rest_space = int(rsp['data']['rest_space'])
        send_space = int(rsp['data']['send_space'])
        storage_space = rest_space + send_space
        print(_('used_space',
            round(send_space / 1024**3, 2),
            round(rest_space / 1024**3, 2),
            round(storage_space / 1024**3, 2)
        ))

    def userinfo():
        global LANG
        s.post(
            url='https://www.wenshushu.cn/ap/user/userinfo',
            json={"plat": "pcweb"}
        )

    def addsend():
        global LANG
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
            print(_('too_fast', rsp["message"]))
            sys.exit(0)
        data = rsp["data"]
        assert data, _('need_verification')
        bid, ufileid, tid = data["bid"], data["ufileid"], data["tid"]
        upId = get_up_id(bid, ufileid, tid, file_size)
        return bid, ufileid, tid, upId

    def get_up_id(bid: str, ufileid: str, tid: str, file_size: int):
        global LANG
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
        global LANG
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
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/copysend',
            json={
                'bid': boxid,
                'tid': taskid,
                'ufileid': preid
            }
        )
        rsp = r.json()
        print(_('personal_link', rsp['data']['mgr_url']))
        print(_('public_link', rsp['data']['public_url']))

    def fast():
        global LANG
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
        for i in range(2):
            r = s.post(
                url='https://www.wenshushu.cn/ap/uploadv2/fast',
                json=payload
            )
            rsp = r.json()
            can_fast = rsp["data"]["status"]
            ufile = rsp['data']['ufile']
            if can_fast and not ufile:
                hash_codes = ''
                for block, partnu in read_file():
                    hash_codes += calc_file_hash("MD5", block)
                payload['hash']['cm'] = sha1_str(hash_codes)
            elif can_fast and ufile:
                print(_('instant_transfer', name))
                getprocess(upId)
                copysend(boxid, taskid, preid)
                sys.exit(0)

        return name, taskid, boxid, preid, upId

    def getprocess(upId: str):
        global LANG
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
        global LANG
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

    def file_put(psurl_args, fn, offset=0, read_size=chunk_size, chunk_index=None):
        global LANG
        # 检查是否被中断
        if upload_interrupted:
            return None
            
        with open(fn, "rb") as fio:
            fio.seek(offset)
            try:
                # 设置较短的超时时间
                response = requests.put(url=psurl(*psurl_args), data=fio.read(read_size), timeout=30)
                response.raise_for_status()
                return chunk_index  # 返回成功上传的分块索引
            except Exception as e:
                if not upload_interrupted:
                    print(f'分块 {chunk_index} 上传失败: {e}')
                raise

    def upload_main():
        global LANG
        fname, tid, boxid, preid, upId = fast()
        
        if ispart:
            print(_('file_chunked_upload'))
            total_chunks = (file_size + chunk_size - 1)//chunk_size
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_list = []
                for i in range(total_chunks):
                    # 检查是否被中断
                    if upload_interrupted:
                        break
                        
                    ul_size = chunk_size if chunk_size*(i+1) <= file_size \
                        else file_size % chunk_size
                    future_list.append(executor.submit(
                        file_put, [fname, upId, ul_size, i+1],
                        filePath, chunk_size*i, ul_size, i+1
                    ))
                
                completed_futures = set()
                count = 0
                start_time = time.time()
                
                try:
                    # 非阻塞式检查完成的任务
                    while len(completed_futures) < len(future_list) and not upload_interrupted:
                        for future in future_list:
                            if future in completed_futures:
                                continue
                                
                            if future.done():
                                completed_futures.add(future)
                                try:
                                    result = future.result()
                                    if result is not None:
                                        count += 1
                                        # 计算已上传大小
                                        uploaded_size = count * chunk_size
                                        if count == total_chunks:
                                            uploaded_size = file_size
                                        
                                        progress_bar = draw_progress_bar(uploaded_size, file_size, start_time=start_time)
                                        print(f'\r{progress_bar}', end='', flush=True)
                                    
                                except Exception as e:
                                    if not upload_interrupted:
                                        print(f'分块上传失败: {e}')
                        
                        # 短暂休眠避免CPU占用过高
                        time.sleep(0.1)
                    
                    # 检查是否被中断
                    if upload_interrupted:
                        print()  # 换行
                        print(_('upload_cancelled'))
                        # 强制取消所有未完成的任务
                        for future in future_list:
                            future.cancel()
                        return
                    
                    # 上传完成
                    if count >= total_chunks:
                        print()  # 换行
                        print(_('upload_complete'))
                            
                except Exception as e:
                    if not upload_interrupted:
                        print(_('upload_error', e))
                    raise
        else:
            print(_('file_single_upload'))
            try:
                file_put([fname, upId, file_size], filePath, 0, file_size)
                if not upload_interrupted:
                    print(_('upload_complete_100'))
            except KeyboardInterrupt:
                print()  # 换行
                print(_('upload_cancelled'))
                return
        
        # 检查是否被中断，如果被中断则不执行完成操作
        if upload_interrupted:
            return

        complete(fname, upId, tid, boxid, preid)
        getprocess(upId)
            
    upload_main()


def test_interrupt():
    """测试中断功能"""
    global upload_interrupted
    
    print("=== Testing Interrupt Handling ===")
    print("This will simulate upload with interrupt capability")
    print("Press Ctrl+C once for graceful exit, twice for force exit")
    
    try:
        for i in range(100):
            if upload_interrupted:
                print("Graceful interrupt detected, exiting...")
                break
            print(f"Simulating upload progress: {i+1}/100", end='\r')
            time.sleep(0.1)
        
        if not upload_interrupted:
            print("\nSimulation completed without interrupt")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught in test function")
    
    print("=== Interrupt Test Complete ===")


def test_translation():
    """测试翻译功能"""
    global LANG
    
    print("=== Testing Translation System ===")
    
    # 测试中文
    LANG = 'zh'
    print(f"Chinese: {_('file_size', 10.5)}")
    print(f"Chinese: {_('download_complete')}")
    
    # 测试英文  
    LANG = 'en'
    print(f"English: {_('file_size', 10.5)}")
    print(f"English: {_('download_complete')}")
    
    print("=== Translation Test Complete ===")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Wenshushu upload/download tool')
    parser.add_argument('action', choices=['upload', 'u', 'download', 'd'], 
                       help='Operation type: upload/u (upload) or download/d (download)')
    parser.add_argument('file_or_url', help='File path (upload) or download link (download)')
    parser.add_argument('-c', '--continue', dest='resume', action='store_true',
                       help='Enable resume (download only)')
    parser.add_argument('-l', '--lang', choices=['zh', 'en'], default='zh',
                       help='Language: zh (Chinese) or en (English), default: zh')
    
    args = parser.parse_args()
    
    # 设置全局语言
    LANG = args.lang
    
    s = requests.Session()
    s.headers['X-TOKEN'] = login_anonymous(s)
    s.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"
    s.headers['Accept-Language'] = "en-US, en;q=0.9"  # NOTE: require header, otherwise return {"code":-1, ...}
    
    try:
        if args.action.lower() in ['upload', 'u']:
            current_operation = 'upload'
            resume_enabled = False  # 上传操作不支持断点续传
            upload(args.file_or_url)
        elif args.action.lower() in ['download', 'd']:
            current_operation = 'download'
            resume_enabled = args.resume
            download(args.file_or_url, args.resume)
    except Exception as e:
        traceback.print_exc()
