from docxtpl import DocxTemplate


def create(cars, data: dict = None, template_file="模板/抄告模版.docx"):
    # 读取模板
    if data is None:
        data = {}
    # 根据城市进行分类
    table_dict = {}
    for car in cars:
        # 如果是赣/渝车牌则跳过
        if car.get('plate_number','').startswith('赣') or car.get('plate_number','').startswith('渝'):
            continue
        # 如果负责人手机存在
        if car.get('telephone') is None and car.get('principalMobile') is not None:
            car['telephone'] = car.get('principalMobile')
        elif car.get('telephone') is not None and car.get('principalMobile') is not None:
            # 如果都不为空,则以/连接联系方式
            car['telephone'] = car.get('telephone') + '/' + car.get('principalMobile')
        if car['city_and_province'] not in table_dict.keys():
            car['index'] = 1
            table_dict[car['city_and_province']] = {'table_data': [car], 'city_and_province': car['city_and_province']}
        else:
            car['index'] = len(table_dict[car['city_and_province']]['table_data']) + 1
            table_dict[car['city_and_province']]['table_data'].append(car)
    for key in table_dict.keys():
        template = DocxTemplate(template_file)
        template.render(table_dict[key])
        # 保存文件
        template.save("抄告/" + key + "抄告.docx")
