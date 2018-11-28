#!/usr/bin/env python
# coding:utf-8

"""
需求：

1、初始化linux环境
2、安装和配置钱包masternode

3、日常监控运行masternode状态，推送状态到服务器（任务）
4、添加新钱包，删除钱包，查看钱包

"""

import argparse
import subprocess
import os
import time
import sys
import socket
import copy
import commands
import json
import datetime
import os


print("install pip and python lib...")
ret = subprocess.call(['apt-get install python-pip python-requests python-virtualenv -y'], shell=True)

import requests
import pickle




############
###全局变量##
############


import sys
reload(sys)
sys.setdefaultencoding('utf-8')



APP_VERSION = "1.0"
GET_CONF_API_URL = "https://mn.bluemn.net/mnapi/getconf"
GET_CONF_API_URL_BK = "http://127.0.0.1/mnapi/getconf"
POST_API_URL = "https://mn.bluemn.net/mnapi/postpk"
ARGS = None
WALLET_LIST = []


############
##初始化##
############


parser = argparse.ArgumentParser(
    description='Process masternode vps setup python script. by BMN TEAM')
parser.add_argument(
    "-i", "--init", help="Install the dependent environment needed for  masternode vps", action="store_true")
parser.add_argument(
    "-c", "--check", help="Check the status of all masternode wallet apps", action="store_true")
parser.add_argument(
    "-l", "--list", help="List all installed masternode states", action="store_true")

parser.add_argument(
    "-a", "--add", help="Add a new wallet deployment", choices=["new", 'all'])
parser.add_argument(
        "-o", "--addone", help="add new wallet deployment", action="store_true")
parser.add_argument(
    "-d", "--remove", help="Delete wallet deployment", action="append")
parser.add_argument(
    "-u", "--update", help="Update all wallet app deployment", action="store_true")
parser.add_argument("-s", "--restart",
                    help="restart all wallet deployment", action="store_true")

parser.add_argument("-p", "--postpk",
                    help="Post pkdata to server", action="store_true")

parser.add_argument("-v", "--version", action="store_true",
                    help="Current version")

args = parser.parse_args()
ARGS = args




############
##基础func##
############

def operation_file(file_name):
    try:
        h_file = open(file_name)
        try:
            readlines = h_file.readlines()
            print(readlines)
        finally:
            h_file.close()
    except IOError:
        print("IOError")


def operation_write_file(file_name, strs):
    try:
        h_file = open(file_name, 'w', 1)
        try:
            h_file.write(strs)
        finally:
            h_file.close()
    except IOError:
        print("IOError")


def operation_add_file(file_name, strs):
    try:
        h_file = open(file_name, 'a+', 1)
        try:
            h_file.write(strs)
        finally:
            h_file.close()
    except IOError:
        print("IOError")


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

def set_pkjson(pk_json_dict=None,cover=False):
    # 格式：生成时间、主机名、vps绑定ip、mn秘钥，绑定端口，钱包缩写、是否已占用。占用交易tx。
    sava_pk = pk_json_dict
    new_pk_list = []

    print("准备保存pkdata.......")
    if pk_json_dict == None:

        print("没有数据，不保存")
        return False
    else:
        # 先读取文件去重
        oldpk_list = load_pkjson("pkdata.json")
        # 没有源文件
        if oldpk_list == []:
           new_pk_list.append(sava_pk)
        else:
            # 有旧版配置文件
            print("存在旧版配置文件")
            print("旧版文件打印：")
            print(oldpk_list)
            print("需要新增的文件")
            print(sava_pk)

            namelist = []
            for pk in oldpk_list:
                namelist.append(pk.get("mncoin"))
            print(namelist)
            is_use = False
            if sava_pk.get("mncoin") in namelist:
                print("需要保存的已经已存在")
                is_use = True


            for old in oldpk_list:
                print("循环构建新列表")
                if is_use:
                    print("存在同coin，覆盖")
                    if old.get("mncoin") == sava_pk.get("mncoin"):
                         new_pk_list.append(sava_pk)
                new_pk_list.append(old)
        print("新的构造list")
        print(new_pk_list)

    # 读取文件 ,设置值,保存
    # jsondata = json.dumps(new_pk_list)
    # operation_write_file('pkdata.json',jsondata)
    dumps_pkjson('pkdata.json',new_pk_list)

    pass

def get_pkjson(file_name="pkdata.json"):

    pk_list = []
    try:
        pkobj = open(file_name,"r")
        try:
            pk_list = json.load(pkobj)
            print(pk_list)
            if type(pk_list) != list:
                print('pkdata.json格式错误，已清空')
                comm = "rm %s " %  file_name
                ret = subprocess.call([comm], shell=True)

        finally:
            pkobj.close()
            return pk_list
    except IOError:
        print("找不到pkdata.json配置文件")

    return pk_list


def dumps_pkjson(filename,strtext):

    with open(filename,'wb') as f:
    #f.write( pickle.dumps(info) )
        pickle.dump(strtext,f)

def load_pkjson(filename):

    # data = pickle.loads(f.read())
    try:
        with open(filename,'rb') as f:
            try:
                data = pickle.load(f)  #跟上面的data = pickle.loads(f.read())语意完全一样。

            except Exception as e:
                print('转换pkjson文件失败,格式错误')
                return []
            else:
                print('data>>>',data)
                if type(data) != list:
                    print('pkdata.json格式非法，已清空')
                    comm = "rm %s " %  filename
                    ret = subprocess.call([comm], shell=True)
                    return []
                return data
    except Exception as e:

        print("获取pkdata.json文件失败，可能没有此文件")


    return []


def post_pkjson(file_name="pkdata.json"):

    post_url = POST_API_URL
    pk_list = []

    pk_list = load_pkjson(file_name)

    try:
        if pk_list !=[]:

            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=post_url, headers=headers, data=json.dumps(pk_list))
        else:
            print("没有数据，没有post")
    except Exception as e:

        print("post pk json 失败")
        raise e

        return False

    return  True

def sent_pkjson(pkdata_dict=None):



    post_url = POST_API_URL

    print("正在POST pkdata数据到服务器...")
    if pkdata_dict and type(pkdata_dict) == dict:
        post_list = [pkdata_dict]

        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=post_url, headers=headers, data=json.dumps(post_list))

        except Exception as e:

            print("post pk json 失败")
            raise e

            return False

    return  True


############
##功能func##
############


def init_env():

    # 基础依赖
    ret = subprocess.call(
        [' apt-get wget curl unzip zip git vim python nano pwgen dnsutils zip  unzip net-tools -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install software-properties-common python-software-properties -y'], shell=True)
    ret = subprocess.call(
        [' add-apt-repository ppa:bitcoin/bitcoin -y'], shell=True)
    ret = subprocess.call(['apt-get update -y'], shell=True)
    ret = subprocess.call(['apt-get upgrade -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install libzmq3-dev libboost-all-dev build-essential  libssl-dev libminiupnpc-dev libevent-dev -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install build-essential libtool autotools-dev automake pkg-config libssl-dev libevent-dev bsdmainutils -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install libboost-all-dev libdb4.8-dev libdb4.8++-dev  libminiupnpc-dev  libzmq3-dev -y'], shell=True)
    ret = subprocess.call(
        [' apt-get install libqt5gui5 libqt5core5a libqt5dbus5 qttools5-dev qttools5-dev-tools libprotobuf-dev protobuf-compiler -y'], shell=True)

    # 虚拟内存
    ret = subprocess.call(['free -h'], shell=True)
    ret = subprocess.call([' fallocate -l 4G /swapfile'], shell=True)
    ret = subprocess.call(['ls -lh /swapfile'], shell=True)
    ret = subprocess.call([' chmod 600 /swapfile'], shell=True)
    ret = subprocess.call([' mkswap /swapfile'], shell=True)
    txt = r"echo \'/swapfile none swap sw 0 0\' |  tee -a /etc/fstab "
    ret = subprocess.call([txt], shell=True)
    txt = ' bash -c \"echo \'vm.swappiness = 10\' >> /etc/sysctl.conf\"'
    ret = subprocess.call([txt], shell=True)
    ret = subprocess.call(['free -h'], shell=True)
    ret = subprocess.call(['echo \"SWAP setup complete...\"'], shell=True)

    return ret


def remove_wallet(wallet_data, delconf=False):

    pass
    wallet_path = wallet_data.get("wallet_path")
    ser_path = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    cli_path = wallet_data.get("wallet_path") + wallet_data.get("clibin")
    tx_path = wallet_data.get("wallet_path") + wallet_data.get("txbin")
    config_path = wallet_data.get("config_path")

    print("正在删除旧版钱包文件...")

    comm = "rm -rf %s " % ser_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "rm -rf %s " % cli_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "rm -rf %s " % tx_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "rm -rf %s " % wallet_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    if delconf == True:

        print("删除钱包配置文件")
        comm = "rm -rf %s " % config_path
        print(comm)
        ret = subprocess.call([comm], shell=True)

        comm = "rm pkdata.json"
        print(comm)
        ret = subprocess.call([comm], shell=True)



    return ret


def stop_wallet(wallet_data):

    wallet_path = wallet_data.get("wallet_path")
    ser_path = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    cli_path = wallet_data.get("wallet_path") + wallet_data.get("clibin")
    tx_path = wallet_data.get("wallet_path") + wallet_data.get("txbin")
    config_path = wallet_data.get("config_path")

    print("正在停止钱包于运行")

    comm = r" netstat -tunlp"
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "%s stop " % cli_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "kill -9 $(ps -ef|grep %s | gawk '$0 !~/grep/ {print $2}' |tr -s '\n' ' ')" % wallet_data.get(
        "servbin")
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = "kill -9 `pgrep %s ` " % wallet_data.get("servbin")
    print(comm)
    ret = subprocess.call([comm], shell=True)

    comm = r" netstat -tunlp"
    print(comm)
    ret = subprocess.call([comm], shell=True)

    return True


def start_wallet(wallet_data):

    wallet_path = wallet_data.get("wallet_path")
    ser_path = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    cli_path = wallet_data.get("wallet_path") + wallet_data.get("clibin")
    tx_path = wallet_data.get("wallet_path") + wallet_data.get("txbin")
    config_path = wallet_data.get("config_path")

    print("启动钱包...")
    comm = "%s -daemon &  " % ser_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    print("等待2分钟，同步网络中...")
    time.sleep(60)

    comm = "%s getinfo " % cli_path
    print(comm)
    ret = subprocess.call([comm], shell=True)

    return True


def add_wallet(wallet_data, cover=False):

    # 路径
    wallet_path = wallet_data.get("wallet_path")
    ser_path = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    cli_path = wallet_data.get("wallet_path") + wallet_data.get("clibin")
    tx_path = wallet_data.get("wallet_path") + wallet_data.get("txbin")
    config_path = wallet_data.get("config_path")
    wallet_conf_path = wallet_data.get("conf_path")

    #
    print(wallet_data)

    # 判断是否强制更新
    # 判断过往钱包是否已经存在
    binpath = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    print("check wallet path : %s" % binpath)
    exists_flag = os.path.exists(binpath)
    print(exists_flag)
    if exists_flag == True:
        print("文件已经存在！")
        if cover == False:
            print("不要求覆盖，推出此钱包更新")
            return False
        else:
            print("强制覆盖新钱包!开始删除再配置")
            stop_wallet(wallet_data)
            remove_wallet(wallet_data,delconf=True)

    # 下载和解压

    if wallet_data.get('type') == "zip":

        comm = "wget " + wallet_data.get("url") + \
            " -O " + wallet_data.get('filename')
        ret = subprocess.call([comm], shell=True)
        # 没有就创建目录
        if os.path.exists(wallet_path) == False:
            comm = "mkdir -p %s " % wallet_path
            ret = subprocess.call([comm], shell=True)

        comm = "unzip -o " + \
            wallet_data.get('filename') + "  -d  /tmp"
        ret = subprocess.call([comm], shell=True)

        # 复制文件到钱包
        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('servbin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)

        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('clibin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)

        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('txbin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)

    elif wallet_data.get('type') == "tar.gz":

        comm = "wget " + wallet_data.get("url") + \
            " -O " + wallet_data.get('filename')
        ret = subprocess.call([comm], shell=True)
        # 没有就创建目录
        if os.path.exists(wallet_path) == False:
            comm = "mkdir -p %s " % wallet_path
            ret = subprocess.call([comm], shell=True)

        comm = " tar -zxvf  " + \
            wallet_data.get('filename') + "  -C  /tmp "
        ret = subprocess.call([comm], shell=True)

        # 复制文件到钱包
        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('servbin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)

        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('clibin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)

        comm = "find /tmp -name '%s' -exec cp {} %s " % (wallet_data.get('txbin'),wallet_path)
        comm = comm + r"\;"
        print(comm)
        ret = subprocess.call([comm], shell=True)



    # 给权限
    comm = " chmod 777 -R %s " %  wallet_data.get('wallet_path')
    ret = subprocess.call([comm], shell=True)

    # 运行钱包、同步网络
    stop_wallet(wallet_data)

    # 配置文件写入，重启钱包
    text = (

        "addnode=node-01.bluemn.net:15003\n"
        "addnode=node-02.bluemn.net:15003\n"
        "addnode=node-03.bluemn.net:15003\n"
        "addnode=node-04.bluemn.net:15003\n"
        "addnode=node-05.bluemn.net:15003\n"
        "addnode=node-06.bluemn.net:15003\n"
        "addnode=node-07.bluemn.net:15003\n"
        "addnode=node-08.bluemn.net:15003\n"
        "addnode=node-09.bluemn.net:15003\n"
        "addnode=node-10.bluemn.net:15003\n"
        "addnode=node-11.bluemn.net:15003\n"
        "addnode=node-12.bluemn.net:15003\n"
        "addnode=node-13.bluemn.net:15003\n"
        "addnode=node-14.bluemn.net:15003\n"
        "addnode=node-15.bluemn.net:15003\n"
        "addnode=node-01.nodes.blue:15003\n"
        "addnode=node-02.nodes.blue:15003\n"
        "addnode=node-03.nodes.blue:15003\n"
        "addnode=node-04.nodes.blue:15003\n"
        "addnode=node-05.nodes.blue:15003\n"
        "addnode=node-06.nodes.blue:15003\n"
        "addnode=node-07.nodes.blue:15003\n"
        "addnode=node-08.nodes.blue:15003\n"
        "addnode=node-09.nodes.blue:15003\n"
        "addnode=node-10.nodes.blue:15003\n"
        "addnode=node-11.nodes.blue:15003\n"
        "addnode=node-12.nodes.blue:15003\n"
        "addnode=node-13.nodes.blue:15003\n"
        "addnode=node-14.nodes.blue:15003\n"
        "server=1 \n"
        "listen=1 \n"
        "maxconnections=256 \n"
        "port=%s \n"
        "daemon=1 \n"
        "rpcport=%s \n"
        "rpcuser=%s \n"
        "rpcpassword=%s \n"
        "rpcallowip=%s \n"
        "%s \n" % (
            wallet_data.get('port'),
            wallet_data.get('rpcport'),
            wallet_data.get('rpcuser'),
            wallet_data.get('rpcpassword'),
            wallet_data.get('rpcallowip'),
            wallet_data.get('nodelist'))
    )

    print("正在写入钱包配置文件...")
    operation_write_file(wallet_conf_path, text)

    # 启动钱包,第一次启动要久一点四件同步
    start_wallet(wallet_data)
    time.sleep(30)

    # 第二次启动,设置模式
    stop_wallet(wallet_data)
    start_wallet(wallet_data)


    # 获取masternode秘钥
    masternode_pk = ''
    print("Making genkey...")
    comm = "%s " % cli_path + " masternode genkey"
    print(comm)
    ret, pk = commands.getstatusoutput(comm)
    if ret == 0:
        masternode_pk = pk
    print(masternode_pk)

    # 获取IP地址
    # 获取本机ip
    ip = get_host_ip()
    print(ip)

    # pk写入配置文件

    print("更新配置文件")
    print(masternode_pk)
    addtext = (
        "masternode=1 \n"
        "masternodeprivkey=%s \n"
        "externalip=%s \n" % (masternode_pk, ip))

    operation_add_file(wallet_conf_path, addtext)
    comm = "cat  %s " % wallet_conf_path
    ret = subprocess.call([comm], shell=True)

    # 保存pk值
    pk_json_dict = {
        "addtime":time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
        "vpsname":socket.gethostname(),
        "mncoin":wallet_data.get("name"),
        "mnip":ip,
        "mnport":wallet_data.get("port"),
        "mnpk":masternode_pk,
        "is_use":0,
        "use_tx":"",
        "is_new":0,
    }

    print(pk_json_dict)
    set_pkjson(pk_json_dict)
    sent_pkjson(pk_json_dict)

    # 重启钱包
    stop_wallet(wallet_data)
    start_wallet(wallet_data)

    # 打印状态
    comm = "%s masternode status " % cli_path
    ret = subprocess.call([comm], shell=True)

    print("钱包安装完成")
    return True


def check_mnstat(wallet_data):

    # 路径
    wallet_path = wallet_data.get("wallet_path")
    ser_path = wallet_data.get("wallet_path") + wallet_data.get("servbin")
    cli_path = wallet_data.get("wallet_path") + wallet_data.get("clibin")
    tx_path = wallet_data.get("wallet_path") + wallet_data.get("txbin")
    config_path = wallet_data.get("config_path")
    wallet_conf_path = wallet_data.get("conf_path")

    comm = "cat %s " % wallet_conf_path
    ret, mnconf = commands.getstatusoutput(comm)

    comm = "%s " % cli_path + " getinfo "
    ret, getinfo = commands.getstatusoutput(comm)
    comm = "%s " % cli_path + " getmininginfo "
    ret, getmininginfo = commands.getstatusoutput(comm)

    comm = "%s " % cli_path + " masternode status "
    ret, mnstat = commands.getstatusoutput(comm)

    print(mnconf)
    print(getinfo)
    print(getmininginfo)
    print(mnstat)

    return ret


def check_all_status(local_config_data):

    # 循环检查状态
    for coin in local_config_data.get('coinlist'):
        print(coin)
        check_mnstat(local_config_data.get(coin.upper()))

    return 0

def get_local_conf():

    conf = []
    try:
        confobj = open("wallet_config.json","r")
        try:
            conf = json.load(confobj)
            print(conf)
        finally:
            confobj.close()
            return conf
    except IOError:
        print("没有配置文件，找不到配置文件")

    return conf


def set_local_config_data(new_conf,filename="wallet_config.json"):

    conf = {}
    try:
        jsondata = json.dumps(new_conf)
    except IOError:
        print("转换json为文本错误")
        return False

    operation_write_file(filename,jsondata)
    print("保存配置文件成功")

    return True


def get_cloud_conf(filename="wallet_config.json"):

    conf = {}
    api_url = GET_CONF_API_URL

    try:
        print("主要API服务器请求数据中...")
        payload = {'IP':get_host_ip(),'VPSNAME':os.name}
        r = requests.get(api_url, params=payload)
        print(r.url)
        try:
            print(r.text)
            conf = json.loads(r.text)

        except Exception as e:
            print("数据格式转换错误")
            return conf
    except Exception as e:
        print("主要api请求错误，启动备用api")
        try:

            payload = {'IP':get_host_ip(),'VPSNAME':socket.gethostname()}
            r = requests.get(GET_CONF_API_URL_BK, params=payload)
            print(r.url)
            try:
                print('备用API服务器返回数据...')
                print(r.text)
                conf = json.loads(r.text)
            except Exception as e:
                print("数据格式转换错误")
                return conf
        except Exception as e:
            print("备用api请求错误")

    return conf



############
###判断程序##
############


def main_app():

    ### 拉取配置文件
    ###
    print("初始化配置文件")
    local_config_data = get_local_conf()
    cloud_config_data = get_cloud_conf()
    pk_config_data = get_pkjson()

    ###
    ###

    print(ARGS)
    if ARGS.version == True:
        print("当前版本:%s" % APP_VERSION)
    if ARGS.update == True:
        print("正在更新脚本...")

    if ARGS.init == True:
        print("正在初始化系统环境...")
        init_env()

    if ARGS.list == True:
        print("所有节点信息")

    if ARGS.add != None:
        print("add wallet ", ARGS.add, " ...")
        # 全部覆盖增加
        cover = False
        if ARGS.add == "all":
            # 写入配置文件
            set_local_config_data(cloud_config_data)
            cover = True

        # 获取最新配置
        cloud_coin_list = cloud_config_data.get('coinlist')

        if local_config_data == []:
            print("没有本地钱包配置文件，使用云端配置文件")
            local_coin_list = cloud_config_data.get('coinlist')
            for coin in cloud_coin_list:
                print("开始添加钱包")
                add_wallet(cloud_config_data.get(coin.upper()), cover=True)


        else:
            print("读取并使用本地钱包配置文件")
            local_coin_list = local_config_data.get('coinlist')

            for coin in cloud_coin_list:

                if cover == False:
                    print("不覆盖")
                    if coin.upper() in local_coin_list:
                        print("钱包已经存在，不覆盖")
                        print("%s is use . no add" % coin.upper())

                    else:

                        print("钱包不存在")
                        print("%s not exist adding..." % coin.upper())
                        print(coin.upper(), cloud_coin_list)
                        add_wallet(cloud_config_data.get(coin.upper()))

                elif cover == True:
                    print("覆盖模式")
                    print("adding %s " % coin)
                    add_wallet(cloud_config_data.get(coin.upper()), cover=True)

        set_local_config_data(cloud_config_data)
        post_pkjson()


    if ARGS.addone != None:

        print("增量更新...")
        print("获取本地配置表")
        local_config_data = get_local_conf()
        print(local_config_data)

        #获取远程
        print("获取远程更新表")
        print(cloud_config_data)
        cloud_coin_list = cloud_config_data.get('coinlist')
        print(cloud_coin_list)

        # 对比数据
        print("对比增量数据")
        needaddlist = set(cloud_coin_list).difference(set(local_config_data))
        needaddlist = list(needaddlist)
        print(needaddlist)

        print("强制更新")
        add_wallet(cloud_config_data.get("BMN"), cover=False)

        # 进行增量更新
        # if len(needaddlist) >= 1:
        #     print("增量更新中")
        #     for coin in needaddlist:
        #         print("coinname:%s" % coin)
        #         print("coindata:")
        #         print(cloud_config_data.get(coin))
        #         print("开始添加钱包程序")
        #         add_wallet(cloud_config_data.get("DOGEC"), cover=False)
        #


    if ARGS.remove != None:
        print("正在删除wallet...")



    if ARGS.check == True:
        print("正在检查状态...")
        check_all_status(local_config_data)


    if ARGS.restart == True:
        print("正在重启所有钱包...")
        for coin in local_config_data.get("coinlist"):
            stop_wallet(local_config_data.get(coin.upper()))
            start_wallet(local_config_data.get(coin.upper()))

    if ARGS.postpk == True:
        print("正在发送pkdata给服务器...")
        post_pkjson()



if __name__ == "__main__":

    main_app()
    pass
