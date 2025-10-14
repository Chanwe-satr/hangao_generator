import json
import os
import sys
import time
import urllib
from datetime import datetime
from http.client import responses

import requests
import pandas
from docxtpl import DocxTemplate
from tqdm import tqdm

import chaogao_creator

session = requests.Session()
f = open('token.txt', 'r')
header = {
    'authorization': f.readline().strip(),
    'cookie': f.readline().strip(),
    'host': '10.56.1.52:8000',
    'referer': 'http://10.56.1.52:8000/tmis-query-web/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}
session.headers.update(header)
# 模板
hangao_template = DocxTemplate("模板/函告模板.docx")
mail_template = DocxTemplate("模板/信封模板.docx")
sms_template = DocxTemplate("模板/短信模板.docx")
# 站点映射
station_mapping = {
    '228': 'G228 K2909+400上行动态检测点',
    '233': 'G233 K1295+600动态检测点',
    '267': 'S267 K0+450动态检测点',
    '242': 'S242 K0+450黑林收费站',
    '204': 'G204 K386+800柘汪收费站',
    '204新': '连云港赣榆G204 K386+804动态检测点',
    '228下行': '连云港赣榆G228 K2909+400动态检测点',
    '402': '连云港赣榆S402 K2+000动态检测点'
}
# 根据轴数获取限重
limit_weight_mapping = {
    '2': '18',
    '3': '25',
    '4': '31',
    '5': '42',
    '6': '49'
}
def get_car_info(car):
    """
    黄色车牌为2
    绿色车牌为5
    """
    card_encode = urllib.parse.quote(car)
    url_template = 'http://10.56.1.52:8000/api/tmis/toi-query/v1/{nations}vehicles/{card_encode}/{card_type}?t={time}'
    nations = '' if car.startswith('苏') else 'nations/'
    url = url_template.format(nations=nations, card_encode=card_encode, card_type=2, time=int(time.time()))
    resp = session.get(url)
    if resp.status_code == 200:
        if not resp.json().get('success'):
            print(f"黄色{car}未找到，正在查询绿色车牌")
            # 获取绿色车牌
            url = url_template.format(nations=nations, card_encode=card_encode,card_type=5, time=int(time.time()))
            resp=session.get(url)
    if resp.status_code != 200 :
        print(f"绿色{car}未找到")
        return None
    return resp.json()

def get_data(card: str):
    """
    获取车辆信息
    :param card:
    :return:
    """
    # time.sleep(1)
    response_data=get_car_info(card)
    if response_data is None:
        return None
    if response_data.get('data') is not None:
        # 获取详细信息
        owner_id = response_data.get('data').get('ownerId')
        provinceCode = response_data.get('data').get('provinceCode')
        if card.startswith('苏'):
            detail_url = f'http://10.56.1.52:8000/api/tmis/toi-query/v1/owners/{owner_id}?t={int(time.time())}'
        else:
            detail_url = f'http://10.56.1.52:8000/api/tmis/toi-query/v1/nations/owners/{provinceCode}/{owner_id}?t={int(time.time())}'
        detail_resp = session.get(detail_url).json()
        owner_name = detail_resp.get('data').get('ownerName')
        principalMobile = detail_resp.get('data').get('principalMobile', None)
        address = detail_resp.get('data').get('address')
        principal = detail_resp.get('data').get('principal')
        telephone = detail_resp.get('data').get('telephone', None)
        return {'owner_name': owner_name,
                'principalMobile': principalMobile,
                "address": address,
                "principal": principal,
                "telephone": telephone
                }
    return None


def get_city_from_car_number(car_number: str):
    """
    获取车牌省份
    :param car_number:
    :return:
    """
    # 获取编码
    code = car_number[0:2]
    with open('card_mapping.json', 'r', encoding='utf-8') as f:
        return json.load(f).get(code)


def generate_file_name(filepath: str) -> str:
    """
    在文件名后添加序号
    :param filepath:
    :return:
    """
    # 如果文件不存在，直接返回原路径
    if not os.path.exists(filepath):
        return filepath

    # 分离文件名和扩展名
    base, ext = os.path.splitext(filepath)
    counter = 1

    # 循环直到找到不存在的文件名
    while True:
        new_filepath = f"{base}_{counter}{ext}"
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1


if not os.path.exists('函告'):
    os.makedirs('函告')
if not os.path.exists('信封'):
    os.makedirs('信封')
if not os.path.exists('短信'):
    os.makedirs('短信')
if not os.path.exists('抄告'):
    os.makedirs('抄告')

if os.path.exists('函告.xls'):
    # 读取 xls 文件
    df = pandas.read_excel('函告.xls')
    print(f"读取 函告.xls 文件成功")
elif os.path.exists('函告.xlsx'):
    # 读取 xlsx 文件
    df = pandas.read_excel('函告.xlsx')
    print(f"读取 '函告.xlsx' 文件成功")
else:
    print("函告.xls 和 函告.xlsx 文件都不存在")
    os.system('pause')
    sys.exit()

case_number = int(input("输入起始案号："))
user_infos = []
chaogao_data = []
ganyu_data = []
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="正在生成"):
    # v_data = {"key":"value"}
    system_data = get_data(row['车牌'])  # 获取车辆信息
    if system_data:
        # 业户信息
        user_info={
            "时间":row['时间'],
            "车牌":row['车牌'],
            "业户名称":system_data.get('owner_name'),
            "是否处罚":"",
            "处理情况":"",
            "桩号":row['桩号'],
            "轴数":row['轴数'],
            "吨位":row['总重T'],
            "地址":system_data.get('address'),
            "负责人":system_data.get('principal'),
            "负责人手机号":system_data.get('principalMobile'),
            "联系电话":system_data.get('telephone')
        }
        user_infos.append(user_info)
        # 案号
        case_number = case_number + 1
        dt = datetime.strptime(row['时间'], '%Y-%m-%d %H:%M:%S.%f')
        data = {
            'plate_number': row['车牌'],
            'case_number': str(case_number),
            'year': str(dt.year),
            'month': str(dt.month),
            'day': str(dt.day),
            'hour': str(dt.hour),
            'minute': str(dt.minute),
            'weight': row['总重T'],
            'station': station_mapping[str(row['桩号'])]
        }
        data.update(system_data)
        # 抄告数据
        city_and_province = get_city_from_car_number(row['车牌'])
        # 如果是赣榆
        if '赣榆' in system_data['address']:
            ganyu_data.append({
                "时间":row['时间'],
                "车牌":row['车牌'],
                "轴数": row['轴数'],
                "总重T": row['总重T'],
                "桩号": row['桩号'],
                "业户":system_data.get('owner_name'),
                "地址":system_data.get('address'),
                "负责人":system_data.get('principal'),
                "负责人手机号":system_data.get('principalMobile'),
                "联系电话":system_data.get('telephone')
            })
        else:
            # 添加到抄告数据
            chaogao_data.append({
                'station': data['station'],
                'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'plate_number': data['plate_number'],
                'owner_name': system_data['owner_name'],
                'telephone': system_data['telephone'],
                'principalMobile': system_data['principalMobile'],
                'weight': row['总重T'],
                'limit_weight': limit_weight_mapping.get(str(row['轴数'])),
                'over_weight': row['超限T'],
                'over_rate': row['超限率%'],
                'city_and_province': city_and_province,
                'address': system_data['address']
            })
        hangao_template.render(data)
        hangao_template.save(generate_file_name(f'函告/{row["车牌"]}.docx'))
        mail_template.render(data)
        mail_template.save(generate_file_name(f'信封/{row["车牌"]}.docx'))
        sms_template.render(data)
        sms_template.save(generate_file_name(f'短信/{row["车牌"]}.docx'))
chaogao_creator.create(chaogao_data)
# 保存业户信息
user_df = pandas.DataFrame(user_infos)
user_df.index = user_df.index + 1
user_df.to_excel('业户信息.xlsx',index_label='序号')
# 保存赣榆数据
ganyu_df = pandas.DataFrame(ganyu_data)
ganyu_df.to_excel('抄告/赣榆抄告.xlsx')
os.system('pause')
