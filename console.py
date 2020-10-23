#!/usr/bin/env python
# coding=utf-8
import webbrowser

from instance.createinstance import AliyunRunInstances
from instance.prepare import Prepare
from instance.releaseinstance import Release

from instance.config import *


def pre_work():
    pre = Prepare()
    accouts = pre.check_money()
    print("当前余额剩余:%.2f" % accouts)
    if accouts < 100:
        url = 'https://usercenter2.aliyun.com/finance/fund-management/recharge'
        webbrowser.open(url)
        print("余额不足，请充值")
        exit(0)
    # 刷新安全组
    if pre.refresh_security_group(True):
        print("安全组刷新成功")


def create_work():
    # 选择机器类型
    instance_machine_type_x = ""

    if instance_machine_type:
        instance_machine_type_x = instance_machine_type
        print("预选了 " + instance_machine_type + " 机器")
    else:
        instance_type = input(
            """\033[1;34m
               选择创建的实例
            * 1. 1C-1G \t  0.065 /时\t ecs.s6-c1m1.small
            * 2. 2C-2G \t  0.095 /时\t ecs.ic5.large
            * 3. 2C-4G \t  0.104 /时\t ecs.c5.large
            * 4. 2C-8G \t  0.131 /时\t ecs.g5.large
            * 5. 4C-8G \t  0.166 /时\t ecs.c5.xlarge
            * 6. 4C-16G \t 0.219 /时\t ecs.g5.xlarge
            * 7. 返回上级
            * >>\033[0m""".replace(" ", "").strip())

        if instance_type == "1":
            instance_machine_type_x = 'ecs.s6-c1m1.small'
        elif instance_type == '2':
            instance_machine_type_x = 'ecs.ic5.large'
        elif instance_type == '3':
            instance_machine_type_x = 'ecs.c5.large'
        elif instance_type == '4':
            instance_machine_type_x = 'ecs.g5.large'
        elif instance_type == '5':
            instance_machine_type_x = 'ecs.c5.xlarge'
        elif instance_type == '6':
            instance_machine_type_x = 'ecs.g5.xlarge'
        elif instance_type == '7':
            return

    # 获取镜像信息
    res = pre.get_image_message()
    if not res or len(res) < 3:
        inputs = input("没有可用镜像,是否启用原生镜像?(y/n): ")
        if inputs == 'y':
            print("使用原生镜像创建实例")
            res = {"hadoop001": "centos_7_8_x64_20G_alibase_20200817.vhd",
                   "hadoop002": "centos_7_8_x64_20G_alibase_20200817.vhd",
                   "hadoop003": "centos_7_8_x64_20G_alibase_20200817.vhd"}
        else:
            print("取消创建...")

    for key in res:
        if key.startswith('hadoop00'):
            print("key:%s value:%s" % (key, res[key]))
            AliyunRunInstances(instance_machine_type_x, res[key], key, key).run()


def delete_instance():
    re = Release()
    # 1. 删除镜像
    re.delete_image()
    # # 2. 删除快照
    re.delete_snapshot()
    # # 3. 创建快照
    diskid = re.desc_insname_diskid(re.desc_instance_disk())
    snapshots = re.create_snapshot(diskid)
    re.desc_snapshot_process(snapshots)
    # 4. 创建镜像
    re.create_image()
    # 5. 释放机器
    re.release_instance()


def force_delete_instance():
    re = Release()
    re.release_instance()


if __name__ == '__main__':

    pre = Prepare()
    release = Release()
    while True:
        input_chars = input(
            """
            \033[1;34m
            | 1. 检查工作
            | 2. 创建实例
            | 3. 查看实例
            | 4. 网络写入
            | 5. 释放实例
            | 6. 直接释放
            | 7. 退出程序
            | > \033[0m""".replace(" ", "").strip())
        if not input_chars.strip():
            print("\n")
            continue
        if input_chars == "1":
            pre_work()
        elif input_chars == "2":
            create_work()
        elif input_chars == "3":
            print("查看")
        elif input_chars == "4":
            if release.desc_instance():
                pre.get_network()
            else:
                print("\033[1;31m" + "当前无实例，添加啥？" + " \033[0m")
        elif input_chars == "5":
            if release.desc_instance():
                delete_instance()
            else:
                print("\033[1;31m" + "当前无实例，还要删？" + " \033[0m")
        elif input_chars == "6":
            force_delete_instance()
        elif input_chars == "7":
            exit(0)
        else:
            print("输入有误，请核对....")
