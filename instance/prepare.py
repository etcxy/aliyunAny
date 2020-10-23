#!/usr/bin/env python
# coding=utf-8

import json
import os
import time
import webbrowser
from urllib.request import urlopen

from aliyunsdkbssopenapi.request.v20171214.QueryAccountBalanceRequest import QueryAccountBalanceRequest
from aliyunsdkecs.request.v20140526.AuthorizeSecurityGroupRequest import AuthorizeSecurityGroupRequest
from aliyunsdkecs.request.v20140526.DescribeImagesRequest import DescribeImagesRequest
from aliyunsdkecs.request.v20140526.RevokeSecurityGroupRequest import RevokeSecurityGroupRequest

from instance.config import *

# 准备操作
from instance.connect import ConnectShell
from instance.running import Running

CHECK_INTERVAL = 3
CHECK_TIMEOUT = 20


class Prepare(object):

    def __init__(self):
        self.client = client

    def check_money(self):
        """
        检查余额
        :return:
        """
        request = QueryAccountBalanceRequest()
        request.set_accept_format('json')

        response = self.client.do_action_with_exception(request)
        res_json = json.loads(str(response, encoding='utf-8'))
        if res_json["Message"] == "success":
            money = res_json["Data"]["AvailableCashAmount"]
            return float(money)
        else:
            return 0

    def refresh_security_group(self, need_delete=False):
        """
        清洗安全组
        :param need_delete:
        :return:
        """
        if need_delete:
            if self.remove_security_group():
                return self.add_security_group()
            else:
                print("删除失败")
                return False
        else:
            return self.add_security_group()

    def get_image_message(self):
        """
        获取镜像信息
        :return:
        """
        request = DescribeImagesRequest()
        request.set_accept_format('json')
        request.set_ImageOwnerAlias("self")
        response = self.client.do_action_with_exception(request)
        d = json.loads(str(response, encoding='utf-8'))

        return {temp_dict['ImageName']: temp_dict['ImageId'] for temp_dict in d['Images']['Image'] if
                temp_dict['ImageOwnerAlias'] == 'self'}

    def remove_security_group(self):
        """
        删除当前安全组规则
        :return:
        """
        request = RevokeSecurityGroupRequest()
        request.set_accept_format('json')

        request.set_SecurityGroupId(security_group_id)
        request.set_PortRange("-1/-1")
        request.set_IpProtocol("all")
        request.set_SourceCidrIp("0.0.0.0/0")

        response = self.client.do_action_with_exception(request)
        # print(str(response, encoding='utf-8'))
        return True if response else not response

    def add_security_group(self):
        """
        获取中控机公网地址
        """
        my_ip: bytes = urlopen('http://ip.42.pl/raw').read()
        print("当前公网IP:" + str(my_ip.decode('utf-8')))

        request = AuthorizeSecurityGroupRequest()
        request.set_accept_format('json')

        request.set_SecurityGroupId(security_group_id)
        request.set_IpProtocol("all")
        request.set_PortRange("-1/-1")
        request.set_SourceCidrIp(my_ip)
        request.set_Policy("accept")
        request.set_Priority("2")
        response = self.client.do_action_with_exception(request)
        return True if response else not response

    def remove_known_hosts(self, public_ip: dict):
        if hosts_known_position:
            host_list = list(public_ip.keys()) + list(public_ip.values())
            for host in host_list:
                os.system("sed -i '' '/'" + host + "'/d' " + hosts_known_position)

    def do_with_public_network(self, public_ip):
        try:
            host_input = open(hosts_position, 'r', encoding=encode)
            host_lines = host_input.readlines()
            host_input.close()

            output = open(hosts_position, 'w')
            for line in host_lines:
                if not line:
                    break
                nb = False
                for key in public_ip:
                    if line.find(key) != -1:
                        nb = True
                        break
                if not nb:
                    output.write(line)
            output.writelines("\n")
            for key in public_ip:
                output.writelines(public_ip[key] + " " + key + "\n")
            output.close()
        except PermissionError as error:
            print("\033[1;31m" + str(error) + " \033[0m")

    def do_with_private_network(self, private_ip):
        str_ip: str = ""
        host_dict = {}

        for hostname in private_ip:
            str_ip += private_ip[hostname] + " " + hostname + "\n"
            ssh = ConnectShell(hostname, "root")
            host_dict.update({hostname: ssh})

        for ssh in host_dict:
            for host_name in private_ip.keys():
                host_dict[ssh].do_action("sed -i \'/" + host_name + "/d\' /etc/hosts")
            host_dict[ssh].do_action("echo \'" + str_ip + "\' >> /etc/hosts")

            print(host_name + "host写入成功")

    def get_network(self):
        # 获取公网，私网
        start = time.time()
        times: int = 0
        while True:
            times += 1
            print("正在第 " + str(times) + " 次查询")
            run = Running()
            public_ip = run.get_public_ips()
            private_ip = run.get_private_ips()
            if public_ip and private_ip:
                print(public_ip)
                self.do_with_public_network(public_ip)
                print(private_ip)
                self.do_with_private_network(private_ip)
                self.remove_known_hosts(public_ip)
                break
            if time.time() - start > CHECK_TIMEOUT:
                print("未检测到实例")
                break
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    pre = Prepare()
    accouts = pre.check_money()
    print("当前余额剩余:%.2f" % accouts)
    if accouts < 100:
        url = 'https://usercenter2.aliyun.com/finance/fund-management/recharge'
        webbrowser.open(url)
        print("余额不足，请充值")
        exit(0)

    pre.refresh_security_group(True)

    res = pre.get_image_message()
    print(res)
