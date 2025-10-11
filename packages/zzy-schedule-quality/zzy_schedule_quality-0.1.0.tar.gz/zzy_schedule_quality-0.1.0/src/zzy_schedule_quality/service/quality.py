import requests
import json
import os
from zzy_schedule_quality.utils import constant


token = '854e0233de8477faabde981469040e24'
tenantId = '217001928145646268'
projectId = '1234560004'

# 请求-质量整改列表
def quality_rectification_list(page_num=1, page_size=20):
    headers = { 
        'Content-Type': 'application/json',
        'Bsp_token': token,
        'Bsp_User_Tenant': tenantId,
    }

    data = {
        "p": page_num,
        "c": page_size,
        "projectId": projectId,
    }

    response = requests.post(
        constant.QUALITY_RECTIFICATION_LIST_URL,
        data=json.dumps(data), 
        headers=headers, 
        verify=  os.environ.get('ENV', '') != 'development'
    )
    list_data = []
    if response.status_code == 200 or response.code=='0':
        print('请求成功')
        # 提取数据
        list_data = extract_list_data(response.json())
        # print(list_data)
    else:
        print('请求失败')

    return list_data

# 定义严重程度字典
severity_dict = {
    0: "一般",
    1: "严重",
    2: "重大"
}

# 提取整改单列表数据
def extract_list_data(res_data):

    records = res_data['data']['list']
    result_str = ''
    for record in records:
        detail = record.get('problemDetail', '')
        level = detail.get('severity', 0)

        result_str += f"id: {record.get('id', '')}, " \
                      f"name: {record.get('name', '')}, " \
                      f"userName: {record.get('checkUserName', '')}, " \
                      f"date: {record.get('checkDate', '')}, " \
                      f"severity: {severity_dict.get(level, '未知')}\n"\
                      f"deadline: {detail.get('rectificationPeriod', '')}\n"
    
    return result_str


# 请求-质量整改详情
def quality_rectification_detail(record_id:str):
    """用于查询质量整改的单条记录详情。返回一个对象，包含了xxx等信息。"""
    headers = { 
        'Content-Type': 'application/json',
        'Bsp_token': token,
        'Bsp_User_Tenant': tenantId,
        "projectId": projectId,
    }
    detail_data = {}
    response = requests.get(constant.QUALITY_RECTIFICATION_DETAIL_URL + record_id, headers=headers)
    if response.status_code == 200:
        print('请求成功')
        res_data = response.json()
        detail_data = extract_detail_data(res_data)
        # TODO-提取数据
        # detail_data = '请求成功'
    else:
        print('请求失败')
    return detail_data

# 提取整改详情数据
def extract_detail_data(res_data):
    record = res_data['data']
    result_str = json.dumps(record)
    return result_str
