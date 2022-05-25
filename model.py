import web, datetime
import time

db = web.database(dbn="mysql", db="kh_erp", host="localhost" , user="root" , password="123456")

def select_table_from_sql(table_name):
    return db.select(table_name,)


# 创建新商品类别【名称 编号】
def insert_info_to_material_category(name, number):

    table_name = "material_category"
    # 判断表中是否存在该条编号
    status = db.select(table_name, where="serial_no=$number", vars=locals())
    if status:
        return -1       # 类别编号已存在

    # 判断表中是否存在该类别名称
    status = db.select(table_name, where="name=$name", vars=locals())
    if status:
        return -2       # 类别名称已存在

    # 存入表中
    status = db.insert(
        table_name, name = name , serial_no = number
    )
    if status:
        return 1        #正常存入
    else :
        return 0       #存入异常


# 创建商品【类别编号 类别名称 商品编号 商品名称 商品单位】
def insert_info_to_kh_material(new_material):

    # 根据类别名称获得类别编号
    category_name = new_material['category_name']
    category_id = db.select("material_category", what='serial_no', where="name=$category_name", vars=locals())[0][
        'serial_no']
    material_id = new_material['material_id']   # 新商品编号
    name = new_material['name']     # 新商品名称
    unit = new_material['unit']     # 新商品单位
    supplier = new_material['supplier'] # 新商品供应商

    '''     1.更改类别表状态       '''
    table_name = "material_category";
    category = db.select(
        table_name, where="serial_no=$category_id AND name=$category_name", vars=locals()
    )

    # 如果存在该条商品，则获取该条商品的状态【0：库存中未入库；1：已入库】
    if category:
        category_status = category[0]['status']
    else:
        return -1  # material_category表中未找到该类别信息

    if (not category_status):
        status = db.update(table_name, where="serial_no=$category_id AND name=$category_name",
                           vars=locals(), status=1)
        if (not status):
            return -2  # 更新material_category表中状态异常


    table_name = "kh_material"

    '''     2.检查商品信息        '''
    # 判断表中是否存在该条编号
    status = db.select(table_name, where="material_id=$material_id", vars=locals())
    if status:
        return -3  # 编号已存在

    # 判断表中是否存在该类别名称
    status = db.select(table_name, where="name=$name", vars=locals())
    if status:
        return -4  # 名称已存在


    '''     3.存入商品表       '''
    status = db.insert(
        table_name, category_id=category_id, category_name=category_name, material_id=material_id, name=name, unit=unit,
        supplier=supplier)
    if (not status):
        return 0  # 更新kh_material表中状态异常

    return 1 # 正常存入


# 创建新项目
def insert_info_to_kh_project(project_id,name):

    table_name = "kh_project" ;
    status = db.insert(
        table_name, project_id = project_id, name = name
    )
    return status


# 检查项目信息并保存 主要判断编号和名称是否重复
def check_project_info(new_project):
    id = new_project['id']
    name = new_project['name']

    get_status = db.select("kh_project", where="project_id=$id", vars=locals())
    if(get_status):
        return -1   # id重复

    get_status = db.select("kh_project", where="name=$name", vars=locals())
    if(get_status):
        return -2    # 名称重复

    status = insert_info_to_kh_project(id, name)
    if(status):
        return 1    # 下发成功
    else:
        return 0    # 下发异常


def delete_info_from_table(table_name,id):
    db.delete(table_name, where="ID=$id", vars=locals())