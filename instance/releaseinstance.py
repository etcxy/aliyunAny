#!/usr/bin/env python
# coding=utf-8
import json
import time

from aliyunsdkecs.request.v20140526.CreateImageRequest import CreateImageRequest
from aliyunsdkecs.request.v20140526.CreateSnapshotRequest import CreateSnapshotRequest
from aliyunsdkecs.request.v20140526.DeleteImageRequest import DeleteImageRequest
from aliyunsdkecs.request.v20140526.DeleteInstancesRequest import DeleteInstancesRequest
from aliyunsdkecs.request.v20140526.DeleteSnapshotRequest import DeleteSnapshotRequest
from aliyunsdkecs.request.v20140526.DescribeDisksRequest import DescribeDisksRequest
from aliyunsdkecs.request.v20140526.DescribeImagesRequest import DescribeImagesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeSnapshotsRequest import DescribeSnapshotsRequest

from instance.config import client


class Release(object):
    """
    释放操作
    """

    def __init__(self):
        self.client = client

    def delete_image(self):
        """
        删除镜像
        :return:
        """
        request = DescribeImagesRequest()
        request.set_accept_format('json')

        response = self.client.do_action_with_exception(request)
        res = json.loads(str(response, encoding='utf-8'))
        for temp_dict in res['Images']['Image']:
            if temp_dict['ImageName'].startswith('hadoop'):
                print(temp_dict['ImageId'])
                delete_request = DeleteImageRequest()
                delete_request.set_accept_format('json')
                delete_request.set_Force(True)
                delete_request.set_ImageId(temp_dict['ImageId'])
                delete_respons = self.client.do_action_with_exception(delete_request)
                print(delete_respons)

    def delete_snapshot(self):
        """
        删除快照
        :return:
        """
        request = DescribeSnapshotsRequest()
        request.set_accept_format('json')

        response = self.client.do_action_with_exception(request)
        res = json.loads(str(response, encoding='utf-8'))
        for temp_dict in res['Snapshots']['Snapshot']:
            if temp_dict['SnapshotName'].startswith('hadoop'):
                print(temp_dict['SnapshotId'])
                delete_request = DeleteSnapshotRequest()
                delete_request.set_accept_format('json')
                delete_request.set_SnapshotId(temp_dict['SnapshotId'])
                delete_respons = self.client.do_action_with_exception(delete_request)
                print(delete_respons)

    def create_snapshot(self, dicts):
        """
        创建快照
        :param dicts:
        :return:
        """
        request = CreateSnapshotRequest()
        request.set_accept_format('json')

        ins2snap = {}
        for key in dicts:
            request.set_DiskId(dicts[key])
            request.set_SnapshotName(key)
            request.set_Description(key)
            request.set_Category("Standard")
            response = self.client.do_action_with_exception(request)
            if response:
                ins2snap.pop(key, json.loads(str(response, encoding='utf-8'))['SnapshotId'])
        return ins2snap

    def create_image(self):
        request = CreateImageRequest()
        request.set_accept_format('json')
        for i in range(1, 4):
            request.set_SnapshotId(self.desc_snapshot("hadoop00" + str(i)))
            request.set_ImageName("hadoop00" + str(i))
            response = self.client.do_action_with_exception(request)
            print(str(response, encoding='utf-8'))

    def desc_snapshot(self, s_name):
        """
        根据snapshot名称，获取snapshot的ID
        :param s_name:
        :return:
        """
        request = DescribeSnapshotsRequest()
        request.set_accept_format('json')
        request.set_SnapshotName(s_name)
        response = self.client.do_action_with_exception(request)
        print(response)
        return json.loads(str(response, encoding='utf-8'))['Snapshots']['Snapshot'][0]['SnapshotId']

    def desc_snapshot_process(self, snap_ids):
        """
        根据snapshot名称，获取快照进度
        :param snap_id:
        :return:
        """
        request = DescribeSnapshotsRequest()
        request.set_accept_format('json')
        str_ids = ""
        for s_ids in snap_ids:
            str_ids += snap_ids[s_ids]

        while True:
            request.set_SnapshotIds(str_ids)
            response = self.client.do_action_with_exception(request)
            json_progress = json.loads(str(response, encoding='utf-8'))
            dict_name_progress = {temp_dicts['SnapshotName']: temp_dicts['Progress'] for temp_dicts in
                                  json_progress['Snapshots']['Snapshot']}
            if not dict_name_progress:
                return
            print(dict_name_progress)
            all_complit = True
            for percent in dict_name_progress.values():
                if percent != '100%':
                    all_complit = False
                    break
            if all_complit:
                return
            time.sleep(3)

    def desc_instance(self):
        desc_instance_request = DescribeInstancesRequest()
        desc_instance_request.set_accept_format('json')
        desc_instance_response = self.client.do_action_with_exception(desc_instance_request)
        loads = json.loads(str(desc_instance_response, encoding='utf-8'))

        return {temp_dicts['InstanceName']: temp_dicts['InstanceId'] for temp_dicts in
                loads['Instances']['Instance'] if
                temp_dicts['InstanceName'].startswith('hadoop')}

    def desc_instance_disk(self):
        """
        描述实例和磁盘对应关系
        :return:
        """
        desc_disk_request = DescribeDisksRequest()
        desc_disk_request.set_accept_format('json')
        desc_disk_response = self.client.do_action_with_exception(desc_disk_request)
        json_loads = json.loads(str(desc_disk_response, encoding='utf-8'))

        for temp_dict in json_loads['Disks']['Disk']:
            print(temp_dict['InstanceId'] + ":" + temp_dict['DiskId'])

        return {temp_dict['InstanceId']: temp_dict['DiskId'] for temp_dict in json_loads['Disks']['Disk']}

    def desc_insname_diskid(self, dicts):
        """
        返回实例名称和磁盘ID的名称
        :param dicts:
        :return:
        """
        desc_instance_request = DescribeInstancesRequest()
        desc_instance_request.set_accept_format('json')
        desc_instance_response = self.client.do_action_with_exception(desc_instance_request)
        loads = json.loads(str(desc_instance_response, encoding='utf-8'))

        return {temp_dicts['InstanceName']: dicts[temp_dicts['InstanceId']] for temp_dicts in
                loads['Instances']['Instance'] if
                temp_dicts['InstanceName'].startswith('hadoop')}

    def release_instance(self):
        dist = self.desc_instance()
        instance_list = list(dist.values())
        request = DeleteInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(instance_list)
        request.set_Force(True)
        response = client.do_action_with_exception(request)
        print(str(response, encoding='utf-8'))



