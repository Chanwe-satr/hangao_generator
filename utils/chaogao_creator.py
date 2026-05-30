from docxtpl import DocxTemplate

def ganyu_chaogao():
    """
    生成赣榆县车辆抄告 ， xlsx格式
    :return:
    """


def create(cars, data: dict = None, template_file="模板/抄告模版.docx"):
    if data is None:
        data = {}
    table_dict = {}
    index_dict = {}
    for car in cars:
        if car.get('telephone') is None and car.get('principalMobile') is not None:
            car['telephone'] = car.get('principalMobile')
        elif car.get('telephone') is not None and car.get('principalMobile') is not None:
            car['telephone'] = car.get('telephone') + '/' + car.get('principalMobile')
        if '赣榆' in car['address']:
            continue
        elif '东海' in car['address']:
            if '东海县' not in table_dict.keys():
                table_dict['东海县'] = {'table_data': [], 'city_and_province': '东海县'}
                index_dict['东海县'] = 0
            index_dict['东海县'] += 1
            car['index'] = index_dict['东海县']
            table_dict['东海县']['table_data'].append(car)
            continue
        elif '灌云' in car['address']:
            if '灌云县' not in table_dict.keys():
                table_dict['灌云县'] = {'table_data': [], 'city_and_province': '灌云县'}
                index_dict['灌云县'] = 0
            index_dict['灌云县'] += 1
            car['index'] = index_dict['灌云县']
            table_dict['灌云县']['table_data'].append(car)
            continue
        elif '灌南' in car['address']:
            if '灌南县' not in table_dict.keys():
                table_dict['灌南县'] = {'table_data': [], 'city_and_province': '灌南县'}
                index_dict['灌南县'] = 0
            index_dict['灌南县'] += 1
            car['index'] = index_dict['灌南县']
            table_dict['灌南县']['table_data'].append(car)
            continue
        if car['city_and_province'] not in table_dict.keys():
            index_dict[car['city_and_province']] = 0
            table_dict[car['city_and_province']] = {'table_data': [], 'city_and_province': car['city_and_province']}
        index_dict[car['city_and_province']] += 1
        car['index'] = index_dict[car['city_and_province']]
        table_dict[car['city_and_province']]['table_data'].append(car)
    for key in table_dict.keys():
        template = DocxTemplate(template_file)
        template.render(table_dict[key])
        template.save("抄告/" + key + "抄告.docx")
