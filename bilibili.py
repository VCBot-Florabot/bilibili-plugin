import json
import yaml
import os
import datetime

from time import sleep,time
#from threading import Timer
from typing import Tuple,Union
from apscheduler.schedulers.blocking import BlockingScheduler
#from loguru import logger
#from ruamel import yaml

from bilibili_api import Credential,login_func,login
from bilibili_api import dynamic,sync
from bilibili_api.user import User,RelationType
from bilibili_api.login_func import QrCodeLoginEvents
from bilibili_api.utils.utils import get_api
from bilibili_api.utils.network import Api
from bilibili_api.exceptions import LoginError


API=get_api("dynamic")
flora_api = {}  # 顾名思义,FloraBot的API,载入(若插件已设为禁用则不载入)后会赋值上
c=Credential()
sche=BlockingScheduler()
last_update = int(time())
tmp_status={}
at_message="\n[CQ:at,qq=all]"
    
class bili_dynamic:
    def get_liveing_users(): #获取正在直播的up(从动态页面获取),wip
        #logger.info('test')
        infos=sync(dynamic.get_live_users(credential=c))
        for i in range(0,9):
            failed=False
            try:
                info=infos['items'][i]
                #print(info)
            except:
                failed=True
            finally:
                if failed:
                    break
                else:
                    u_cfg={}
                    tml_status_bak=json.load(open(f'./{flora_api.get("ThePluginPath")}/data/bkstatus.json',mode='r',errors='ignore'))
                    #print(tml_status_bak)
                    tmp_status[info['uid']]=True
                    with open(f'./{flora_api.get("ThePluginPath")}/data/bkstatus.json',mode='w',errors='ignore')as f:
                        f.write(json.dumps(tmp_status))
                    try:
                        u_cfg=config[str(info['uid'])]['gid']
                        #print(u_cfg)
                    except:
                        continue
                    finally:
                        try:
                            a=tml_status_bak[str(info['uid'])]
                            #print(a)
                        except:
                            
                            msg=f'{info["uname"]} 正在直播！\n{bili_dynamic.clean_url(info["link"])}'
                            if config[str(info['uid'])]['atall']['live'] is True:
                                msg+=at_message
                            for g in u_cfg:
                                send_compatible(msg=msg,gid=g,uid=g)
                        finally:
                            continue

    def parse_dynamic(d: dict):
        info = d['modules']['module_author']
        dtype = d['type']
        image = ""
        if dtype == 'DYNAMIC_TYPE_AV':
            # 投稿了视频
            content = d['modules']['module_dynamic']['major']['archive']
            text = info['pub_action'] + ': ' + content['title']
            image= content['cover']
            url = content['jump_url']
        elif dtype in ['DYNAMIC_TYPE_DRAW', 'DYNAMIC_TYPE_WORD']:
            # 发送了图文动态
            url = d['basic']['jump_url']
            text = '发布动态：' + d['modules']['module_dynamic']['major']['opus']['summary']['text']
        elif dtype == 'DYNAMIC_TYPE_ARTICLE':
            # 投稿专栏
            url = d['basic']['jump_url']
            text = info['pub_action'] + ': ' + d['modules']['module_dynamic']['major']['opus']['title']
        elif dtype == 'DYNAMIC_TYPE_FORWARD':
            # 转发
            url = '//t.bilibili.com/' + d['basic']['comment_id_str']
            text = '转发了：' + d['modules']['module_dynamic']['desc']['text']
        else:
            url = ''
            text = '未识别动态种类：' + dtype
        #print(text)
        return {
            'mid': info['mid'],
            'name': info['name'],
            'type': dtype,
            'time': int(info['pub_ts']),
            'text': text,
            'image': image,
            'url': ('https:' + url) if len(url) else ''
        }
    def fetch_bilibili_updates():
        global last_update

        #logger.debug('test')
        #if len(config.items()) == 0:
        #    return
        #logger.debug('获取B站动态更新')
        try:
            dyna = sync( custom_bili_API.get_dynamic_page_info(credential=c))
        except:
            #logger.error('获取B站动态更新失败')

            return
        #logger.debug(f'更新到{len(dyna)}条动态')
        dyna_names = []
        dyna_times = []
        for i, d in enumerate(dyna):
            #logger.debug(f'处理第{i + 1}条动态')
            #logger.debug(d)
            res = bili_dynamic.parse_dynamic(d)
            #屏蔽标题带‘直播回放‘
            if res['text'].find('直播回放')!=-1:
                continue
            #logger.debug(res)
            dyna_names.append(res['name'])
            failed=False
            #logger.debug(f'Time: {datetime.datetime.fromtimestamp(res["time"])}({res["time"]}) vs {last_update}')
            try:
                dd=config[str(res['mid'])]
            except KeyError:
                failed=True
                #logger.debug(f'{res["mid"]}未在配置文件中找到')
            
            if not failed and res['time'] > last_update : #
                print('test')
                print(last_update)
                dtype = res['mid']
                print('test')
                #if is_in_blacklist(key, dtype):
                #    continue
                if res['type'] == "DYNAMIC_TYPE_AV":
                    msg = f"{res['name']} {bili_dynamic.shorten(res['text'])}\n[CQ:image,file={res['image']}]\n{bili_dynamic.clean_url(res['url'])}"
                    if config[str(res['mid'])]['atall']['video'] is True:
                        msg+=at_message
                else:
                    msg = f"{res['name']} {bili_dynamic.shorten(res['text'])}\n{bili_dynamic.clean_url(res['url'])}"
                    if config[str(res['mid'])]['atall']['dynamic'] is True:
                        msg+=at_message
                for gid in config[str(res['mid'])]['gid']:
                    #if is_in_blacklist(gid, dtype):
                    #   continue
                    #logger.info(f'将{key}的更新推送到{gid}\n{msg}')
                    #await MessageFactory(msg).send_to(TargetQQGroup(group_id=int(gid)))
                    send_compatible(msg=msg,gid=gid,uid=gid)
            dyna_times.append(res["time"])
        if (t:= max(dyna_times)) != last_update: # 使用最后一条动态的时间
            last_update = t
            with open(tmp_save, 'w') as f:
                json.dump({'last_update': t}, f)
            #logger.debug(f'刷新动态更新时间为{t}({last_update})')
        #logger.debug(f'成功刷新{len(dyna)}条动态：' + ', '.join(dyna_names))`
        #dynamic_event.start()
        


    def clean_url(u: str) -> str:
        return u.split('?')[0]

    def shorten(u: str) -> str:
        l = 255
        if len(u) > l:
            return u[:l] + '\n...点击链接查看全文'
        return u

    def dynamics():
        try:
            bili_dynamic.get_liveing_users()
            bili_dynamic.fetch_bilibili_updates()
        except:
            pass

class configs:
    def init():
        try:
            config=yaml.load(open(file=f"./{flora_api.get('ThePluginPath')}/data/config.yml",encoding="utf-8").read(),Loader=yaml.FullLoader)
        except:
            config={}
            with open(file=f"./{flora_api.get('ThePluginPath')}/data/config.yml",mode="w",encoding="utf-8") as config_file:
                config_file.write(yaml.dump(data=config))
        finally:
            return config
    def update():
        with open(file=f"./{flora_api.get('ThePluginPath')}/data/config.yml",mode="w",encoding="utf-8") as config_file:
            config_file.write(yaml.dump(config))


class custom_bili_API: 
    async def get_dynamic_page_info(credential: Credential,features: str ="itemOpusStyle",pn: int =1):
        api=API["info"]['dynamic_page_info']
        params ={
            "timezone_offset": -400,
            "features": features,
            "pn": pn
        }
        dynamic_data=(
            await Api(**api,credential=credential).update_params(**params).result
        )
        return dynamic_data['items']

    
    def check_qrcode_events(login_key: str) -> Tuple[QrCodeLoginEvents, Union[str, Credential]]: 
        #因为(https://github.com/Nemo2011/bilibili-api/issues/755),所以手动把修复后的API代码搬到这里
        events = login.login_with_key(login_key)

        if events["code"] == 86101:
            return QrCodeLoginEvents.SCAN, events["message"]
        elif events["code"] == 86090:
            return QrCodeLoginEvents.CONF, events["message"]
        elif events["code"] == 86038:
            return QrCodeLoginEvents.TIMEOUT, events["message"]
        elif events["code"] == 0:
            url: str = events["url"]
            cookies_list = url.split("?")[1].split("&")
            sessdata = ""
            bili_jct = ""
            dede = ""
            for cookie in cookies_list:
                if cookie[:8] == "SESSDATA":
                    sessdata = cookie[9:]
                if cookie[:8] == "bili_jct":
                    bili_jct = cookie[9:]
                if cookie[:11].upper() == "DEDEUSERID=":
                    dede = cookie[11:]
            c = Credential(sessdata, bili_jct, dedeuserid=dede)
            return QrCodeLoginEvents.DONE, c
        else:
            raise LoginError(events["message"])

def occupying_function(*values):  # 该函数仅用于占位,并没有任何意义
    pass


send_msg = occupying_function


def init():  # 插件初始化函数,在载入(若插件已设为禁用则不载入)或启用插件时会调用一次,API可能没有那么快更新,可等待,无传入参数
    global send_msg
    global loaded
    global live_stat
    global dynamic_event

    global tmp_save
    tmp_save = f"./{flora_api.get('ThePluginPath')}/data/last_update.json"
    global last_update
    loaded=False
    #print(flora_api)
    send_msg = flora_api.get("SendMsg")
    #创建data文件夹
    if not os.path.exists(f"./{flora_api.get('ThePluginPath')}/data"):
        os.mkdir(f"./{flora_api.get('ThePluginPath')}/data")
        with open(f'./{flora_api.get("ThePluginPath")}/data/bkstatus.json',mode='w',errors='ignore') as f:
            f.write('{}')
    print("Bilibili-plugin 加载成功")
    login_failed=False
    global config
    config=configs.init()
    try:
        cook=json.load(open(file=f"./{flora_api.get('ThePluginPath')}/data/cookie.json",encoding="utf-8"))
        global c
        c=Credential(sessdata=cook['SESSDATA'],bili_jct=cook['bili_jct'],dedeuserid=cook['DedeUserID'])
    except:
        print("未检测到cookie,请先登录!")
        login_failed=True
    finally:
        if not login_failed and not loaded:
            sche.add_job(bili_dynamic.dynamics, 'interval', seconds=10)
            sche.start()
        else:
            return

    try:
        with open(tmp_save, 'r') as f:
            last_update = json.load(f)['last_update']
        dt = datetime.datetime.fromtimestamp(last_update)
        print(f'加载上次更新时间{dt}({last_update})')
    except:
        #logger.warning('未找到上次更新时间，使用当前时间')
        last_update = int(time())


def api_update_event():  # 在API更新时会调用一次(若插件已设为禁用则不调用),可及时获得最新的API内容,无传入参数
    #print(flora_api)

    pass


def event(data: dict):  # 事件函数,FloraBot每收到一个事件都会调用这个函数(若插件已设为禁用则不调用),传入原消息JSON参数
    print(data)

    uid = data.get("user_id")  # 事件对象QQ号
    gid = data.get("group_id")  # 事件对象群号
    mid = data.get("message_id")  # 消息ID
    msg = data.get("raw_message")  # 消息内容
    try:
        global ws_client
        global ws_server
        send_address = data.get("SendAddress")
        ws_client = send_address.get("WebSocketClient")
        ws_server = send_address.get("WebSocketServer")
    except:
        ws_server=None
        ws_client = None
        pass
    if msg is not None:
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")  # 消息需要将URL编码替换到正确内容
        print(uid, gid, mid, msg)
        if msg == "Btest":
            print(config.items())
            print(config.values())
        if msg == "B登录":
            if uid not in flora_api.get('Administrator') and gid is None: # 判断是否为Bot管理员且在私聊
                return
            log_data=login_func.get_qrcode() #Tuple[Picture,key]
            token=log_data[1]
            send_compatible(msg=f"请扫描二维码登录\n[CQ:image,file={log_data[0].url}]",uid=uid,gid=gid)
            while True:
                sleep(1)
                result=custom_bili_API.check_qrcode_events(token)
                if result[0] is QrCodeLoginEvents.DONE:
                    cookies=result[1]
                    print(cookies)
                    with open(file=f"./{flora_api.get('ThePluginPath')}/data/cookie.json",mode="w",encoding="utf-8",errors="ignore") as cookies_file:
                        cookies_file.write(json.dumps(cookies.get_cookies(),ensure_ascii=False))
                    send_compatible(msg="登录成功",uid=uid,gid=gid)
                    restart=flora_api.get("LoadPlugins")
                    restart()
                    break
        message=msg.split(" ")
        if message[0] == "B订阅" and gid is not None:
            u=User(uid=message[1],credential=c)
            i=sync(u.get_relation(message[1]))
            print(i)
            if i['relation']['attribute'] == 0: #判断是否为关注,0为未关注
                sync(u.modify_relation(relation=RelationType.SUBSCRIBE)) #修改为关注
            failed=False
            u_cfg=[]
            try:
                u_cfg=config[message[1]]
            except:
                failed=True
                config[message[1]]={
                        "gid":[],
                        "atall":{
                            "dynamic": False,
                            "video": False,
                            "live": False
                        }
                    }
                u_cfg=config[message[1]]
            finally:
                if failed and not gid in u_cfg['gid']:
                    u_cfg['gid'].append(gid)
                elif gid in u_cfg['gid']:
                    send_compatible(msg="已订阅过此用户",uid=uid,gid=gid)
                    return
            configs.update()
            send_compatible(msg=f"已订阅{message[1]}",uid=uid,gid=gid)
            return
        if message[0] == "B取消订阅" and gid is not None:
            u_cfg=[]
            failed=False
            try:
                u_cfg=config[message[1]] #list
            except TypeError:
                failed=True
            finally:
                if failed or not gid in u_cfg['gid']:
                    send_compatible(msg="未订阅此用户",uid=uid,gid=gid)
                    return
            if not failed:
                if gid in u_cfg['gid']:
                    config[message[1]]['gid'].remove(gid)
                    configs.update()
                    send_compatible(msg=f"已取消订阅{message[1]}",uid=uid,gid=gid)
                else:
                    send_compatible(msg="未订阅此用户",uid=uid,gid=gid)
                    return
        if message[0] == "B全员" and gid is not None:
            u_cfg=[]
            failed=False
            try:
                types=str(message[2])
            except:
                failed=True
                send_compatible(msg="请输入类型",uid=uid,gid=gid)    
            finally:
                if failed:
                    return
            type_t=["动态","视频","直播"]
            type=["dynamic","video","live"]
            if types not in type and types not in type_t:
                send_compatible(msg="请输入正确的类型",uid=uid,gid=gid)
                return
            else:
                if types in type_t:
                    types=type[type_t.index(types)]


            try:
                u_cfg=config[message[1]]
            except TypeError:
                failed=True
            finally:
                if failed or not gid in u_cfg['gid']:
                    send_compatible(msg="未订阅此用户",uid=uid,gid=gid)
                    return
                elif gid in u_cfg['gid']:
                    cfg=config[message[1]]['atall'][types]
                    if cfg:
                        config[message[1]]['atall'][types]=False
                        send_compatible(msg=f"取消了{message[1]}的{types}全员通知",uid=uid,gid=gid)
                    else:
                        config[message[1]]['atall'][types]=True
                        send_compatible(msg=f"开启了{message[1]}的{types}全员通知",uid=uid,gid=gid)
                    configs.update()


def send_compatible(msg:str,gid:str|int,uid: str|int,data: dict=None):  #兼容性函数,用于兼容旧版本API
    if flora_api.get("FloraVersion") == 'v1.01':
        send_msg(msg=msg,gid=gid,uid=uid)
    else:
        send_type=flora_api.get("ConnectionType")
        send_address=flora_api.get("FrameworkAddress")
        send_msg(msg=msg,gid=gid,uid=uid,send_type=send_type,ws_client=ws_client,ws_server=ws_server)
        