import json
import os
import time
import urllib.parse
from datetime import datetime
from typing import Callable

import pandas
import requests
from docxtpl import DocxTemplate
from urllib3.exceptions import InsecureRequestWarning

import utils.chaogao_creator as chaogao_creator

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GeneratorBackend:
    def __init__(
        self,
        log_callback: Callable[[str], None] = None,
        progress_callback: Callable[[int, int, str], None] = None,
    ):
        self._log = log_callback or (lambda msg: None)
        self._progress = progress_callback or (lambda cur, tot, msg: None)
        self._cancel_flag = False

        self.session: requests.Session | None = None
        self._df: pandas.DataFrame | None = None
        self._case_number: int = 0
        self._user_infos: list[dict] = []
        self._chaogao_data: list[dict] = []
        self._ganyu_data: list[dict] = []
        self._card_mapping: dict[str, str] = {}

        self._station_mapping = {
            '228': 'G228 K2909+400上行动态检测点',
            '233': 'G233 K1295+600动态检测点',
            '267': 'S267 K0+450动态检测点',
            '242': 'S242 K0+450黑林收费站',
            '204': 'G204 K386+800柘汪收费站',
            '204新': '连云港赣榆G204 K386+804动态检测点',
            '228下行': '连云港赣榆G228 K2909+400动态检测点',
            '402': '连云港赣榆S402 K2+000动态检测点',
        }

        self._limit_weight_mapping = {
            '2': '18',
            '3': '25',
            '4': '31',
            '5': '42',
            '6': '49',
        }

        self._template_dir = "模板"

    # --- lifecycle ---

    def load_token(self, token_text: str) -> None:
        cookie = token_text.strip()
        if not cookie:
            raise ValueError("cookie 不能为空")

        self.session = requests.Session()
        self.session.headers.update({
            'cookie': cookie,
            'host': '172.27.10.176:8000',
            'referer': 'http://172.27.10.176:8000/tmis-query-web/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        })

    def set_template_dir(self, path: str) -> None:
        self._template_dir = path

    def load_card_mapping(self, mapping_path: str = "card_mapping.json") -> None:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            self._card_mapping = json.load(f)

    def load_excel(self, excel_path: str) -> int:
        path = excel_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Excel文件不存在: {path}")
        self._df = pandas.read_excel(path)
        self._log(f"读取 {os.path.basename(path)} 成功: {len(self._df)} 条记录")
        return len(self._df)

    def set_case_number(self, number: int) -> None:
        self._case_number = number

    def cancel(self) -> None:
        self._cancel_flag = True

    # --- main processing ---

    def process_all(self) -> None:
        if self._df is None:
            raise RuntimeError("未加载Excel文件，请先调用 load_excel()")
        if self.session is None:
            raise RuntimeError("未加载token，请先调用 load_token()")
        if not self._card_mapping:
            raise RuntimeError("未加载车牌映射，请先调用 load_card_mapping()")

        self._ensure_output_dirs()
        self._user_infos = []
        self._chaogao_data = []
        self._ganyu_data = []

        total = len(self._df)
        td = self._template_dir
        hangao_template = DocxTemplate(f"{td}/函告模板.docx")
        mail_template = DocxTemplate(f"{td}/信封模板.docx")
        sms_template = DocxTemplate(f"{td}/短信模板.docx")

        for idx, (_, row) in enumerate(self._df.iterrows()):
            if self._cancel_flag:
                self._log("用户取消处理")
                return

            plate = row['车牌']
            self._progress(idx + 1, total, plate)

            system_data = self._get_data(plate)
            if system_data is None:
                self._log(f"{plate} 获取车辆信息失败，跳过")
                continue

            self._case_number += 1
            self._render_one_row(
                row, system_data, idx,
                hangao_template, mail_template, sms_template,
            )

        chaogao_creator.create(self._chaogao_data)

        user_df = pandas.DataFrame(self._user_infos)
        user_df.index = user_df.index + 1
        user_df.to_excel('业户信息.xlsx', index_label='序号')
        self._log("业户信息.xlsx 已保存")

        ganyu_df = pandas.DataFrame(self._ganyu_data)
        ganyu_df.to_excel('抄告/赣榆抄告.xlsx')
        self._log("抄告/赣榆抄告.xlsx 已保存")

        self._log(f"处理完成，共 {len(self._user_infos)} 条记录")

    # --- internal helpers ---

    def _ensure_output_dirs(self) -> None:
        for d in ['函告', '信封', '短信', '抄告']:
            os.makedirs(d, exist_ok=True)

    def _get_car_info(self, car: str) -> dict | None:
        card_type_map = {'2': '黄色', '5': '绿色', '6': '黄绿'}
        for key, value in card_type_map.items():
            card_encode = urllib.parse.quote(car)
            nations = '' if car.startswith('苏') else 'nations/'
            url = f'https://172.27.10.176:8000/api/tmis/toi-query/v1/{nations}vehicles/{card_encode}/{key}?t={int(time.time())}'
            resp = self.session.get(url, verify=False)
            if resp.status_code == 200:
                if resp.json().get('data'):
                    self._log(f'{value}-{car} 获取车辆信息成功')
                    return resp.json()
            else:
                self._log(f'{value}-{car} 获取车辆信息失败')
        return None

    def _get_data(self, card: str) -> dict | None:
        response_data = self._get_car_info(card)
        if response_data is None:
            return None
        if response_data.get('data') is not None:
            owner_id = response_data['data']['ownerId']
            province_code = response_data['data']['provinceCode']
            if card.startswith('苏'):
                detail_url = f'https://172.27.10.176:8000/api/tmis/toi-query/v1/owners/{owner_id}?t={int(time.time())}'
            else:
                detail_url = f'https://172.27.10.176:8000/api/tmis/toi-query/v1/nations/owners/{province_code}/{owner_id}?t={int(time.time())}'
            detail_resp = self.session.get(detail_url, verify=False).json()
            data = detail_resp.get('data')
            return {
                'owner_name': data.get('ownerName'),
                'principalMobile': data.get('principalMobile'),
                'address': data.get('address'),
                'principal': data.get('principal'),
                'telephone': data.get('telephone'),
            }
        return None

    def _get_city_from_car_number(self, car_number: str) -> str | None:
        code = car_number[0:2]
        return self._card_mapping.get(code)

    def _generate_file_name(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return filepath
        base, ext = os.path.splitext(filepath)
        counter = 1
        while True:
            new_filepath = f"{base}_{counter}{ext}"
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1

    def _render_one_row(
        self, row, system_data: dict, idx: int,
        hangao_template: DocxTemplate,
        mail_template: DocxTemplate,
        sms_template: DocxTemplate,
    ) -> None:
        plate = row['车牌']
        dt = datetime.strptime(str(row['时间']), '%Y-%m-%d %H:%M:%S.%f')

        data = {
            'plate_number': plate,
            'case_number': str(self._case_number),
            'year': str(dt.year),
            'month': str(dt.month),
            'day': str(dt.day),
            'hour': str(dt.hour),
            'minute': str(dt.minute),
            'weight': row['总重T'],
            'station': self._station_mapping[str(row['桩号'])],
        }
        data.update(system_data)

        city_and_province = self._get_city_from_car_number(plate)

        if '赣榆' in system_data.get('address', ''):
            self._ganyu_data.append({
                '时间': row['时间'],
                '车牌': plate,
                '轴数': row['轴数'],
                '总重T': row['总重T'],
                '桩号': row['桩号'],
                '业户': system_data.get('owner_name'),
                '地址': system_data.get('address'),
                '负责人': system_data.get('principal'),
                '负责人手机号': system_data.get('principalMobile'),
                '联系电话': system_data.get('telephone'),
            })
        else:
            self._chaogao_data.append({
                'station': data['station'],
                'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'plate_number': plate,
                'owner_name': system_data['owner_name'],
                'telephone': system_data['telephone'],
                'principalMobile': system_data['principalMobile'],
                'weight': row['总重T'],
                'limit_weight': self._limit_weight_mapping.get(str(row['轴数'])),
                'over_weight': row['超限T'],
                'over_rate': row['超限率%'],
                'city_and_province': city_and_province,
                'address': system_data['address'],
            })

        self._user_infos.append({
            '时间': row['时间'],
            '车牌': plate,
            '业户名称': system_data.get('owner_name'),
            '是否处罚': '',
            '处理情况': '',
            '桩号': row['桩号'],
            '轴数': row['轴数'],
            '吨位': row['总重T'],
            '地址': system_data.get('address'),
            '负责人': system_data.get('principal'),
            '负责人手机号': system_data.get('principalMobile'),
            '联系电话': system_data.get('telephone'),
        })

        hangao_template.render(data)
        hangao_template.save(self._generate_file_name(f'函告/{plate}.docx'))
        mail_template.render(data)
        mail_template.save(self._generate_file_name(f'信封/{plate}.docx'))
        sms_template.render(data)
        sms_template.save(self._generate_file_name(f'短信/{plate}.docx'))

        self._log(f'{plate} 函告/信封/短信已生成')
