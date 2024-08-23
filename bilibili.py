import json
import os
import sqlite3
import base64

from time import sleep
from threading import Timer

from bilibili_api import Credential,login_func,sync
from bilibili_api import dynamic,live
from bilibili_api.user import User,RelationType
from bilibili_api.login_func import QrCodeLoginEvents

flora_api = {}  # 顾名思义,FloraBot的API,载入(若插件已设为禁用则不载入)后会赋值上


def occupying_function(*values):  # 该函数仅用于占位,并没有任何意义
    pass


send_msg = occupying_function


def init():  # 插件初始化函数,在载入(若插件已设为禁用则不载入)或启用插件时会调用一次,API可能没有那么快更新,可等待,无传入参数
    global send_msg
    #print(flora_api)
    send_msg = flora_api.get("SendMsg")
    #创建data文件夹
    if not os.path.exists(f"./{flora_api.get('ThePluginPath')}/data"):
        os.mkdir(f"./{flora_api.get('ThePluginPath')}/data")
    print("FloraBot插件模板 加载成功")
    login_failed=False
    try:
        cook=json.load(open(file=f"./{flora_api.get('ThePluginPath')}/data/cookie.json",encoding="utf-8"))
        global c
        c=Credential(sessdata=cook['SESSDATA'],bili_jct=cook['bili_jct'],dedeuserid=cook['DedeUserID'])
    except:
        print("未检测到cookie,请先登录")
        login_failed=True
    finally:
        if not login_failed:
            global live_stat
            live_stat=Timer(5,bili_dynamic.get_liveing_users)
            live_stat.setDaemon(False)
            live_stat.run()

def api_update_event():  # 在API更新时会调用一次(若插件已设为禁用则不调用),可及时获得最新的API内容,无传入参数
    #print(flora_api)
    pass


def event(data: dict):  # 事件函数,FloraBot每收到一个事件都会调用这个函数(若插件已设为禁用则不调用),传入原消息JSON参数
    print(data)
    uid = data.get("user_id")  # 事件对象QQ号
    gid = data.get("group_id")  # 事件对象群号
    mid = data.get("message_id")  # 消息ID
    msg = data.get("raw_message")  # 消息内容
    if msg is not None:
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")  # 消息需要将URL编码替换到正确内容
        print(uid, gid, mid, msg)
        if msg == "测试":
            send_msg(msg="测试成功",uid=uid,gid=gid)
        if msg == "登录":
            if uid not in flora_api.get('Administrator') and gid is None: # 判断是否为管理员且在私聊
                return
            log_data=login_func.get_qrcode() #Tuple[Picture,key]
            token=log_data[1]
            send_msg(msg=f"请扫描二维码登录\n[CQ:image,file={log_data[0].url}]",uid=uid,gid=gid)
            while True:
                sleep(1)
                result=login_func.check_qrcode_events(token)
                if result[0] is QrCodeLoginEvents.DONE:
                    cookies=result[1]
                    print(cookies)
                    with open(file=f"./{flora_api.get('ThePluginPath')}/data/cookie.json",mode="w",encoding="utf-8",errors="ignore") as cookies_file:
                        cookies_file.write(json.dumps(cookies.get_cookies(),ensure_ascii=False))
                    send_msg(msg="登录成功",uid=uid,gid=gid)
                    restart=flora_api.get("LoadPlugins")
                    restart()
                    break
        message=msg.split(" ")
        if message[0] == "订阅up":
            u=User(uid=message[1],credential=c)
            i=sync(u.get_relation(message[1]))
            print(i)
            if i['relation']['attribute'] == 0: #判断是否为关注
                sync(u.modify_relation(relation=RelationType.SUBSCRIBE))
            send_msg(msg=f"已订阅{message[1]}",uid=uid,gid=gid)
            return
        

def image_to_base64(image_path:str):
    if image_path.startswith("file://"):
        image_path.replace("file://","")
    with open(image_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        return base64_data

class bili_dynamic:
    def get_liveing_users(): #获取正在直播的up(从动态页面获取),wip
        infos=sync(dynamic.get_live_users(credential=c))
        for i in range(0,9):
            failed=False
            try:
                info=infos['items'][i]
            except:
                failed=True
            finally:
                if failed:
                    break
                else:
                    
                    continue
        live_stat=Timer(5,bili_dynamic.get_liveing_users)
        live_stat.start()

