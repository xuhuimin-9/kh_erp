import web, datetime
import time
from decimal import Decimal
from datetime import datetime

db = web.database(dbn="mysql", db="kh_erp", host="localhost" , user="root" , password="123456")

# 根据表名查询表数据
def select_table_from_sql(table_name):
    return db.select(table_name)

# 插入库存表 目前不用
def insert_info_to_material_io_storage_info(category_id, material_id, name, unit, count, price, tax,tax_price):
    table_name = "material_io_storage_info";
    db.insert(
        table_name, category_id=category_id, material_id=material_id, name=name, unit=unit, count=count, price=price,
        tax_rate=tax, tax_price=tax_price
    )

# 更新商品表数量 目前不用
def update_count_to_kh_material(category_id,material_id,unit,count):
    table_name = "kh_material";
    current_count = db.select(
        table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit", vars=locals()
    )[0]['count']
    new_count = int(current_count) + int(count);
    db.update(table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit",
              vars=locals(), count=new_count)

# 商品入库
def material_in_storage(current_material):

    category_id = current_material['categoryId']
    category_name = current_material['categoryName']
    material_id = current_material['materialId']
    name = current_material['materialName']
    unit = current_material['materialUnit']
    count = current_material['materialCount']
    price = current_material['materialPrice']
    tax = current_material['materialTax']
    tax_price = current_material['materialTaxPrice']

    '''kh_material不将累计数量存在该表中
    # 更新商品库存数量
    table_name = "kh_material";
    # 商品表中商品信息
    material = db.select(
        table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit", vars=locals()
    )
    if (not material):
        return 0;  # 商品表中无该条信息
    # 该条商品信息的当前数量
    current_count = material[0]['count'];
    new_count = int(current_count) + int(count);
    status = db.update(table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit",
                          vars=locals(), count=new_count)
    if (not status):
        return -1;  # 插入kh_material失败'''

    '''     1.存入库存信息表       '''
    table_name = "material_io_storage_info";
    status = db.insert(
        table_name, category_id=category_id, category_name=category_name, material_id=material_id, name=name, unit=unit,
        count=count, price=price,
        tax_rate=tax, tax_price=tax_price
    )
    if(not status):
        return -2 # 插入material_io_storage_info失败

    '''     2.存入入库日志表       '''
    table_name = "material_in_storage_log";
    status = db.insert(
        table_name, category_id=category_id, category_name=category_name, material_id=material_id, name=name, unit=unit,
        count=count, price=price,tax_rate=tax, tax_price=tax_price
    )
    if (not status):
        return -3  # 插入material_in_storage_log失败

    '''     3.更改商品表状态       '''
    table_name = "kh_material";
    material = db.select(
        table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit", vars=locals()
    )
    # 如果存在该条商品，则获取该条商品的状态【0：库存中未入库；1：已入库】
    if material :
        material_status = material[0]['status'];
    else:
        return -4   # kh_material表中未找到该商品信息
    if (not material_status ):
        status = db.update(table_name, where="category_id=$category_id AND material_id=$material_id AND unit = $unit",
                           vars=locals(), status=1)
        if (not status) :
            return -5   # 更新kh_material表中状态异常

    return 1;


# 商品出库
def material_out_storage(current_material):

    # 该id为material_io_storage_info表的中唯一id，非商品id
    id = current_material['id']
    # 出库数量
    outCount = current_material['outCount']
    # 所用项目
    project = current_material['project']

    '''     1.更新库存信息【数量、含税总价】        '''
    table_name = "material_io_storage_info";
    value = db.select(table_name, where="id=$id", vars=locals())
    if (not value):
        return -1  # 商品表中无该条信息
    # webpy的sql结果只能遍历一次，转为list可重复使用
    material = list(value);

    # 该条商品信息的当前信息
    current_count = material[0]['count'];
    new_count = int(current_count) - int(outCount);# 当前数量减去出库数量

    # 该条商品的入库金额
    current_tax_price = material[0]['tax_price'];
    new_tax_price = current_tax_price / current_count * new_count;  # 获得原先含税单价并乘上现有个数

    status = db.update(table_name, where="id=$id",vars=locals(), count=new_count,tax_price=new_tax_price)
    if (not status):
        return -2;  # kh_material更新失败'''


    '''     2.存入出库日志表       '''
    print(material[0])
    category_id = material[0]['category_id']
    category_name = material[0]['category_name']
    material_id = material[0]['material_id']
    name = material[0]['name']
    unit = material[0]['unit']
    price = material[0]['price']
    tax = material[0]['tax_rate']
    value = float(Decimal(str(1 + tax)) * Decimal(str(price)))  #单个含税价
    tax_price = float(Decimal(str(value * int(outCount))))

    table_name = "material_out_storage_log";
    status = db.insert(
        table_name, category_id=category_id, category_name=category_name, material_id=material_id, name=name, unit=unit,
        count=outCount, price=price,tax_rate=tax, tax_price=tax_price, project=project
    )
    if (not status):
        return -4  # 插入material_in_storage_log失败

    '''     3.更新到项目表中 material_id字段值 【含义：商品id 商品名 商品数量 出库时间】        '''
    table_name = "kh_project";

    # 包含当前日期和时间的datetime对象
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y/%m/%d-%H:%M:%S")

    value = db.select(table_name, where="name=$project", vars=locals())[0]['material_id']
    value = value + str(material_id) + " " + name + " " + outCount + " " + dt_string +";"

    status = db.update(table_name, where="name=$project",vars=locals(), material_id=value)
    if (not status):
        return -5  # 插入kh_project失败

    return 1;