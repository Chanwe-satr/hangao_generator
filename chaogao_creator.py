from docxtpl import DocxTemplate


def create(cars, data:dict=None, template_file="模板/抄告模版.docx"):
    # 读取模板
    if data is None:
        data = {}
    # 根据城市进行分类
    table_dict = {}
    for car in cars:
        if car['city_and_province'] not in table_dict.keys():
            car['index'] =1
            table_dict[car['city_and_province']] = {'table_data': [car], 'city_and_province': car['city_and_province']}
        else:
            car['index'] = len(table_dict[car['city_and_province']]['table_data'])+1
            table_dict[car['city_and_province']]['table_data'].append(car)
    for key in table_dict.keys():
        template = DocxTemplate(template_file)
        template.render(table_dict[key])
        # 保存文件
        template.save("抄告/"+key+"抄告.docx")

