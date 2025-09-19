import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

with open('设置.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
    print(f"开始时间为{setting['开始时间']},结束时间为{setting['结束时间']}")
with open('cookie.txt', 'r', encoding='utf-8') as f:
    cookie = f.read()

base_url = 'http://10.54.216.98'

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Cookie': cookie
})


def get_XSRF():
    """
    获取XSRF
    """
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': f'{base_url}/zcweb/Home',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cookie': '.AspNetCore.Antiforgery.MVHJP96rvcg=CfDJ8IvXp2WpNo1Eo1Ti5_IX9fkJ_lnxfSCR0pFfrmjXwzAuXu2ensfWHsb1mfT3lMoK9iZKQ5O8fhpCmz1JVkeVRpxNDKycIp0kWfWBX3JTKKe1b1sjujrK7fuDm7ZXSe9NstVWZh6BNpoIRhnVDzdUhmo; .AspNetCore.Cookies=CfDJ8IvXp2WpNo1Eo1Ti5_IX9fmCU4_E0NrW9WvxwY5g3CW05690gz97tjMuyTBmGhZX6OBU2fSYx9NSh_WwjYHEhehMvNJAXGAJmteUhn0ECP9rvfxI0GOmainw0bwwHMDJa3KpVdxMTepqcJUW6gg0X-K_a1vYjxfyBO7oxgpPYhej4Wg3qOh7tjpAMoyxCngdresQF3d2zKhWHi7nheXxqtd1DM_HLMrHjLVoFAc2dl24VsopYVLCP9P1E_OoQdAJ0LBYlFuVfzZvbNnwUyEwrEZ5v6UOn1NHMvcz8VJC1UinYd110Vz17RFTsxDcneluT7RgROMu8iubiUkxDi4Yt18bURSeED4xa2HRO3DZM8jayWiyIxKdubIdiom9fxMefp0HTopNmFqaQwvMWgQTDSWp9tyH3BY2W0MF05P5UKqyh4yEvUsuHsFr6rN8R77Yl4qFW_vntq1NFBZbQ-u4qv4zj3F-xkKQw5r9zDC6Rl6cF8yf0Oq0AfXp8YaJTG4BYcLDZYBEQq7OG0zGW2cb2FA; .AspNetCore.Session=CfDJ8IvXp2WpNo1Eo1Ti5%2FIX9flJZCtkhUo2M7MtRFXNCSj5p04yCdoMOlgmcHcX%2BXhxWJukcr1OY10pWFUMTgDHMdoBtNGh7odx0wVdhO%2FoyTyn8tMxTiYJTVHqQ%2Fb4XtxBQxqSfO9of7579EF8kcYTPMFZX49n1Cpw30qUA8GBsE20',
    }

    params = {
        'ST': '1',
    }

    response = session.get(
        base_url + '/zcweb/DataQuery/CheckOrder',
        params=params,
        headers=headers,
        verify=False,
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find_all('script', attrs={'type': 'text/javascript'})[-1]
    # 获取文本
    script_text = script_tag.text
    # 解析XSRF
    match = re.search(r'XSRF[^>]+value="([^"]+)"', script_text)
    if match:
        xsrf_value = match.group(1)
        print(xsrf_value)
    else:
        raise Exception("获取XSRF失败")
    return xsrf_value


def parse_search_result(res: dict):
    """
    解析搜索结果
    """
    data = res.get('Data', {})
    tableData = data.get('tableData', {})
    rows = tableData.get('rows', [])
    car_list = []
    for row in rows:
        SystemNO = row.get('SystemNO', '')
        ct = row.get('CheckType', '')
        wd = row.get('PassTime', '')
        car_list.append({
            'SystemNO': SystemNO,
            'CheckType': ct,
            'PassTime': wd,
        })
    return car_list


def search(page_index, station_id, plate_type, start_time=None, end_time=None, weightOS: int = 0):
    """
    搜索
    :param weightOS: 超限
    :param start_time: 开始时间 格式 yyyy-MM-dd HH:mm:ss
    :param end_time: 结束时间 格式 yyyy-MM-dd HH:mm:ss
    :param station_id: 车站ID
    :param plate_type: 车牌类型 0:全部 1:识别 2:未识别

    :return:
    """
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': base_url,
        'Referer': f'{base_url}/zcweb/DataQuery/CheckOrder?ST=3',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    data = {
        'pageIndex': page_index,
        'pageSize': '10',
        'st': '1',
        'startTime': start_time,
        'endTime': end_time,
        'stationId': station_id,
        'roadId': '',
        'plateNo': '',
        'plateType': plate_type,
        'weightOS': weightOS,
        'axisNum': '',
        'startT': '',
        'endT': '',
        'complex': '',
        'minCondfidence': '',
        'maxCondfidence': '',
        'minSpeed': '',
        'maxSpeed': '',
        'plateColor': '',
        'drivingStatus': '',
        'XSRF': XSRF
    }

    response = session.post(
        base_url + '/zcweb/DataQuery/CheckOrderList',
        headers=headers,
        data=data,
        verify=False,
    )
    print(base_url)
    if response.status_code != 200:
        raise Exception(f"搜索失败，状态码为{response.status_code},请检查cookie是否过期")
    return response.json()


def get_photo(res: str):
    """
    获取照片
    res: 详情页的html文档
    :return:
    """
    soup = BeautifulSoup(res, 'html.parser')
    # 解析时间
    titleTable2 = soup.find('table', id='titleTable2')
    # 第一个label为时间
    time_label = titleTable2.find_all('label')[0]
    time_str = time_label.text.strip().replace(":", "：")
    if os.path.exists(time_str):
        os.rmdir(time_str)
    os.mkdir(time_str)
    # 图片table
    img_table = soup.find('table', id='bodyTable')
    # 图片td
    img_tds = img_table.find_all('td', class_='tdImg')
    # 遍历图片td
    for img_td in img_tds:
        img_tag = img_td.find('img', class_='resImg')
        if img_tag is None:
            continue
        pic_name = img_tag['alt']
        if pic_name == '无资源':
            continue
        url = base_url + img_tag['src']
        resp = session.get(url)
        with open(f"{time_str}/{pic_name}.jpg", 'wb') as f:
            f.write(resp.content)


def get_detail(SystemNO: str, wd: str, ct: str = "1"):
    """
    获取照片详情
    _id: 车辆ID
    ct: 不清楚含义默认为1
    wd: 时间
    CheckOrderRes
    """
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': f'{base_url}/zcweb/Home',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    params = {
        'ID': SystemNO,
        'CT': ct,
        'WD': wd,
    }

    response = session.get(
        base_url + '/zcweb/DataQuery/CheckOrderRes',
        params=params,
        headers=headers,
        verify=False,
    )
    return response.text


if __name__ == '__main__':

    print("""请选择站点""")
    print("1. 连云港赣榆G233动态检测点")
    print("2. 连云港赣榆S267动态检测点")
    print("3. 连云港赣榆G204动态检测点")
    print("4. 连云港赣榆G228动态检测点下行")
    print("5. 连云港赣榆S402动态检测点")
    print("6. 204柘汪收费站")
    station_map = {
        "1": "3207210042",
        "2": "3207210043",
        "3": "3207210044",
        "4": "3207210045",
        "5": "3207210046",
        "6": "3207210080"
    }
    station_str = input("请输入站点编号回车键确定：")
    station_id = station_map[station_str]
    if station_id == station_map["6"]:
        base_url = "http://10.54.192.5"
    print("""请车牌识别""")
    print("1. 所有")
    print("2. 已识别")
    print("3. 未识别")
    plate_type_str = input("请输入车牌类型编号回车键确定：")
    print("车辆超限")
    print("1. 所有")
    print("2. 未超限")
    print("3. 超限大于0%")
    print("4. 超限大于5%")
    print("5. 超限大于10%")
    print("6. 超限大于15%")
    print("7. 超限大于20%")
    print("8. 超限大于30%")
    print("9. 超限大于50%")
    print("10. 超限大于100%")
    weightOS_str = input("请输入车辆超限编号回车键确定：")
    weightOS = int(weightOS_str) - 1
    XSRF = get_XSRF()
    plate_type = int(plate_type_str) - 1
    start_time = setting['开始时间']
    end_time = setting['结束时间']
    current_page = 1
    end = False
    while not end:
        search_resp = search(current_page, station_id, plate_type, start_time, end_time, weightOS=weightOS)
        print(f"正在下载第{current_page}页，总计{search_resp.get('Data', {}).get('totalPage', 0)}页")
        # 解析搜索结果
        car_list = parse_search_result(search_resp)
        # 遍历车辆列表
        for car in car_list:
            # 获取车辆详情
            detail_res = get_detail(car['SystemNO'], car['PassTime'], car['CheckType'])
            # 获取照片
            get_photo(detail_res)
        # 翻页
        end = (current_page >= int(search_resp.get('Data', {}).get('totalPage', 1)))
        current_page += 1
    print("下载完成")
    os.system("pause")
