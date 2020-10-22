#!/usr/bin/env python
# coding=utf-8
import json

from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from instance.config import client


# 获取所有实例运行状态信息
class Running(object):

    def __init__(self):
        self.client = client
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        response = self.client.do_action_with_exception(request)
        self.des = json.loads(str(response, encoding='utf-8'))

    def get_private_ips(self):
        """
        返回私网
        :return:
        """
        return {temp_dict['HostName']: temp_dict['VpcAttributes']['PrivateIpAddress']['IpAddress'][0] for temp_dict
                in self.des['Instances']['Instance']
                if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}

    def get_public_ips(self):
        """
        返回公网
        :return:
        """
        return {temp_dict['HostName']: temp_dict['PublicIpAddress']['IpAddress'][0] for temp_dict
                in self.des['Instances']['Instance']
                if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}


if __name__ == '__main__':
    """
    测试使用
    """
    run = Running()
    print(run.get_private_ips())
    print(run.get_public_ips())
