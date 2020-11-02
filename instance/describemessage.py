import json

from aliyunsdkecs.request.v20140526.DescribeInstanceStatusRequest import DescribeInstanceStatusRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

from instance.config import client


def describe_instance_status(instances_ids):
    """
    描述主机状态
    :param instances_ids
            ["i-bp18vj2il5r8z2epa3r0","i-bp1915fj4otwclp73zxl"]
    :return:
            [{'Status': 'Stopped', 'InstanceId': 'i-bp18vj2il5r8z2epa3r0'}, {'Status': 'Stopped', 'InstanceId': 'i-bp1915fj4otwclp73zxl'}]
    """
    request = DescribeInstanceStatusRequest()
    request.set_accept_format('json')
    request.set_InstanceIds(instances_ids)
    response = client.do_action_with_exception(request)
    ss = json.loads(response, encoding='utf-8')
    return ss["InstanceStatuses"]["InstanceStatus"]


def describe_instance():
    desc_instance_request = DescribeInstancesRequest()
    desc_instance_request.set_accept_format('json')
    desc_instance_response = client.do_action_with_exception(desc_instance_request)
    loads = json.loads(str(desc_instance_response, encoding='utf-8'))

    return {temp_dicts['InstanceName']: temp_dicts['InstanceId'] for temp_dicts in
            loads['Instances']['Instance'] if
            temp_dicts['InstanceName'].startswith('hadoop')}

