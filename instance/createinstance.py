#!/usr/bin/env python
# coding=utf-8
import json
import time
import traceback

from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest

from instance.config import *

RUNNING_STATUS = 'Running'
CHECK_INTERVAL = 3
CHECK_TIMEOUT = 180


class AliyunRunInstances(object):

    def __init__(self, instance_type, image_id, instance_name, host_name):

        # 是否只预检此次请求。true：发送检查请求，不会创建实例，也不会产生费用；false：发送正常请求，通过检查后直接创建实例，并直接产生费用
        self.dry_run = False
        # 实例所属的地域ID
        self.region_id = location
        # 实例的资源规格
        self.instance_type = instance_type
        # 实例的计费方式
        self.instance_charge_type = 'PostPaid'
        # 镜像ID
        self.image_id = image_id
        # 指定新创建实例所属于的安全组ID
        self.security_group_id = security_group_id
        # 购买资源的时长
        self.period = 1
        # 购买资源的时长单位
        self.period_unit = 'Hourly'
        # 实例所属的可用区编号
        self.zone_id = 'random'
        # 网络计费类型
        self.internet_charge_type = 'PayByTraffic'
        # 虚拟交换机ID
        self.vswitch_id = vswitch_id
        # 实例名称
        self.instance_name = instance_name
        # 是否使用镜像预设的密码
        self.password_inherit = True
        # 指定创建ECS实例的数量
        self.amount = 1
        # 公网出带宽最大值
        self.internet_max_bandwidth_out = 100
        # 云服务器的主机名
        self.host_name = host_name
        # 是否为I/O优化实例
        self.io_optimized = 'optimized'
        # 密钥对名称
        self.key_pair_name = key_pair
        # 后付费实例的抢占策略
        self.spot_strategy = 'SpotAsPriceGo'
        # 系统盘大小
        self.system_disk_size = '40'
        # 系统盘的磁盘种类
        self.system_disk_category = 'cloud_efficiency'
        self.client = client

    def run(self):
        try:
            ids = self.run_instances()
            # self._check_instances_status(ids)
            return ids
        except ClientException as e:
            print('Fail. Something with your connection with Aliyun go incorrect.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except ServerException as e:
            print('Fail. Business error.'
                  ' Code: {code}, Message: {msg}'
                  .format(code=e.error_code, msg=e.message))
        except Exception:
            print('Unhandled error')
            print(traceback.format_exc())

    def run_instances(self):
        """
        调用创建实例的API，得到实例ID后继续查询实例状态
        :return:instance_ids 需要检查的实例ID
        """
        request = RunInstancesRequest()

        request.set_DryRun(self.dry_run)

        request.set_InstanceType(self.instance_type)
        request.set_InstanceChargeType(self.instance_charge_type)
        request.set_ImageId(self.image_id)
        request.set_SecurityGroupId(self.security_group_id)
        request.set_Period(self.period)
        request.set_KeyPairName(self.key_pair_name)
        request.set_PeriodUnit(self.period_unit)
        request.set_ZoneId(self.zone_id)
        request.set_InternetChargeType(self.internet_charge_type)
        request.set_VSwitchId(self.vswitch_id)
        request.set_InstanceName(self.instance_name)
        request.set_PasswordInherit(self.password_inherit)
        request.set_Amount(self.amount)
        request.set_InternetMaxBandwidthOut(self.internet_max_bandwidth_out)
        request.set_HostName(self.host_name)
        request.set_IoOptimized(self.io_optimized)
        request.set_SpotStrategy(self.spot_strategy)
        request.set_SystemDiskSize(self.system_disk_size)
        request.set_SystemDiskCategory(self.system_disk_category)

        body = self.client.do_action_with_exception(request)
        data = json.loads(body)
        instance_ids = data['InstanceIdSets']['InstanceIdSet']
        print('Success. Instance creation succeed. InstanceIds: {}'.format(', '.join(instance_ids)))
        return instance_ids

    def get_ips(self):
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        response = self.client.do_action_with_exception(request)
        des = json.loads(str(response, encoding='utf-8'))
        return {temp_dict['HostName']: temp_dict['VpcAttributes']['PrivateIpAddress']['IpAddress'][0] for temp_dict
                in des['Instances']['Instance']
                if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}, {
                   temp_dict['HostName']: temp_dict['PublicIpAddress']['IpAddress'][0] for temp_dict
                   in des['Instances']['Instance']
                   if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}

    def _check_instances_status(self, instance_ids):
        """
        每3秒中检查一次实例的状态，超时时间设为3分钟。
        :param instance_ids 需要检查的实例ID
        :return:
        """
        start = time.time()
        while True:
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            response = self.client.do_action_with_exception(request)
            des = json.loads(str(response, encoding='utf-8'))

            if des is not None:
                print('Instances all boot successfully')
                s1 = {temp_dict['HostName']: temp_dict['VpcAttributes']['PrivateIpAddress']['IpAddress'][0] for
                      temp_dict
                      in des['Instances']['Instance']
                      if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}, {
                         temp_dict['HostName']: temp_dict['PublicIpAddress']['IpAddress'][0] for temp_dict
                         in des['Instances']['Instance']
                         if temp_dict['HostName'].startswith('hadoop') and temp_dict['Status'] == 'Running'}
                print(s1)
                break

            if time.time() - start > CHECK_TIMEOUT:
                print("over")
                break

            time.sleep(CHECK_INTERVAL)
