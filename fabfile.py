# coding:utf=8
from fabric.api import run, env


env.hosts= [

    # "155.94.148.80",#vps1 # 搞定
    # "192.210.152.140",#vps2 # 搞定
    # "192.210.152.142",#vps3
    # "192.210.152.143",#vps4
    # "192.210.152.145",#vps5
    # "192.3.116.252",#vps6
    # "192.3.116.254",#vps7



]

# 11.23日更新,选稳定性好一些的节点
env.hosts=[



    "23.94.62.57",#vps7 no
    "23.94.43.140",#vps8 no
    "23.94.43.141",#
    "23.94.43.145",#vps4
    "23.94.43.86",#vps5
    "155.94.154.116",#vps6
    "155.94.154.118",#vps7
    "155.94.154.117",#vps7
    "23.94.43.86",#vps7
    "155.94.154.12",#vps7
    "155.94.154.116",#vps7
    "155.94.154.12",#vps7
    "23.94.43.232",#vps7

]

# 11.24日更新,选稳定性好一些的节点
env.hosts=[


    "192.210.160.54",#vps7 no
    "23.94.43.69",#vps8 no
    "23.94.43.68",#
    "167.160.191.207",#vps4
    "192.3.116.254",#vps5
    "192.3.116.252",#vps6
    "192.3.115.76",#vps7
    "192.161.179.49",#vps7
    "192.161.179.193",#vps7

]
# 11.26日更新,选稳定性好一些的节点
env.hosts=[

    "192.161.179.128",# bmn
    "167.160.191.195",# bmn
    "192.161.179.185",# bmn

    "155.94.154.69",# bmn dogec
    "155.94.154.68",# bmn dogec


]
# # # 11.27日更新,选稳定性好一些的节点
env.hosts=[


    # "181.215.242.77",# bmn dogec
    "155.94.154.208", #
    "155.94.154.133", #
    "23.94.43.7", #
    "23.94.43.25", #
    "23.94.43.24", #
    # "23.94.43.24", #

]

# # # 11.27日更新,选稳定性好一些的节点
env.hosts=[


    # "181.215.242.77",# bmn dogec
    "155.94.154.208", #
    "155.94.154.133", #
    "23.94.43.7", #
    "23.94.43.25", #
    "23.94.43.24", #
    # "23.94.43.24", #

]
#     "23.94.43.24",#vps1
#     "155.94.154.208",#vps2
#     "155.94.154.68",#vps3
#     "155.94.154.69",#vps4


# ]

env.user = 'root'
env.password = 'bbs8886342'
env.warn_only = True

def hello():
    run('ls -l /root/')


def initvps():

    # 删除旧版脚本
    run("rm ~/vpstool -r")


    # 下载脚本
    run("apt-get update")
    run("dpkg --configure -a")
    run("apt-get install python-pip python-requests python-virtualenv git unzip ufw -y")
    run("ufw disable")
    run("git clone https://git.dev.tencent.com/ygyg503/bmn_linux.git vpstool")
    run("cd vpstool")
    run("pwd")


    # 运行脚本
    run("python ~/vpstool/mnmanagement.py --init")

    pass

def removebmn():
    run("rm ~/.bluemncore/ -rf")

def checkbmn():
    run("cd /root/wallet/bmn")
    run("./bluemn-cli getinfo")
    run("./bluemn-cli masternode status")
    run("./bluemn-cli masternodelist")



def deployvps():

    run("python ~/vpstool/mnmanagement.py --add all")
    run("python ~/vpstool/mnmanagement.py --check")

def addnode():

    run("python ~/vpstool/mnmanagement.py --addone")
    run("python ~/vpstool/mnmanagement.py --check")


def initenv():
    run("apt-get update --fix-missing")
    run("dpkg --configure -a")
    run("apt-get install python-pip python-requests -y")
