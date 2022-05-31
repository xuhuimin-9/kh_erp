#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from datetime import date, datetime

import web
import json
import time
import model
import storage
import json
import pymysql

db = web.database(dbn="mysql", db="kh_erp", host="localhost" , user="root" , password="123456")


urls = (
    "/","Index",
    "/view/(\d+)" , "View",
    "/new", "New",

    "/Api", "Api",

    "/materialCategory", "MaterialCategory",
    "/material", "Material",
    "/project", "Project",

    "/deleteMaterial/(\d+)" , "DeleteMaterial",
    "/deleteCategory/(\d+)" , "DeleteCategory",
    "/deleteProject/(\d+)" , "DeleteProject",
    "/deleteInStorageLog/(\d+)", "DeleteInStorageLog",

    "/storageInfo", "StorageInfo",
    "/inStorage", "InStorage",
    "/outStorage", "OutStorage",

    "/categoryChange", "CategoryChange",
    "/categoryNameChange", "CategoryNameChange",

    "/materialChange", "MaterialChange",
    "/materialNameChange", "MaterialNameChange",

    "/filterMaterial", "FilterMaterial",
    "/searchMaterial" , "SearchMaterial",
    "/typeChange", "TypeChange",

    "/inStorageLog", "InStorageLog",
    "/outStorageLog", "OutStorageLog",
    "/storageLogExport", "StorageLogExport",
    "/storageLogfilter", "StorageLogfilter",
    
    "/projecInfo", "ProjecInfo",
    "/materialBorrow", "MaterialBorrow",
    "/stockInfo","StockInfo"


)


t_globals = {"datestr": web.datestr}
render = web.template.render("templates", base="base", globals=t_globals)

def firstDayOfMonth(dt):
    """判断今天是不是这个月第一天"""
    now_day = (dt + datetime.timedelta(days=-dt.day + 1)).day
    return now_day == dt.day

# python识别不了日期格式，转换成str格式
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


# 获取类别信息 和 新建类别信息
class MaterialCategory:
    def GET(self):
        material_category = model.select_table_from_sql("material_category")
        time.sleep(0.5)
        return render.MaterialCategory(list(material_category))

    def POST(self):
        new_material_category = web.input()
        name = new_material_category['name']
        category_id = new_material_category['number']

        status = model.insert_info_to_material_category(name, category_id)

        result = {
            0: "存入异常，请联系后台人员！",
            1: "已存入！",
            -1: "类别编号重复",
            -2: "类别名称重复"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value,ensure_ascii=False)


# 获取商品信息 和 新建商品信息
class Material:
    def GET(self):
        category = list(model.select_table_from_sql("material_category"))
        material = list(model.select_table_from_sql("kh_material"))
        time.sleep(0.5)
        return render.Material(category,material)

    def POST(self):
        new_material = web.input()
        status = model.insert_info_to_kh_material(new_material)

        result = {
            0: "存入异常，请联系后台人员！",
            1: "已存入！",
            -1: "类别表中未找到该类别",
            -2: "更新类别状态异常，请联系后台人员！",
            -3: "商品编号重复",
            -4: "商品名称重复"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value, ensure_ascii=False)


# 获取项目信息 和 创建项目信息
class Project:
    def GET(self):
        """ all project show """
        projects = model.select_table_from_sql("kh_project")
        time.sleep(0.5)
        return render.Project(list(projects))

    def POST(self):
        new_project = web.input()
        status = model.check_project_info(new_project)

        result = {
            0: "存入异常，请联系后台人员！",
            1: "已存入！",
            -1: "项目编号重复",
            -2: "项目名称重复"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value, ensure_ascii=False)

class ProjecInfo:
    def POST(self):
        data = json.loads(web.data())
        project_name = data["projectName"]
        value = db.select("kh_project_material",where="project_name=$project_name", vars=locals())
        material = list(value)
        result = {}
        if(not value):
            result['status'] = 'FAIL'
            result['project_material'] = {}
        else:
            result['status'] = 'SUCCESS'
            result['project_material'] = material

        return json.dumps(result,cls=ComplexEncoder)



# 删除商品信息
class DeleteMaterial:
    def POST(self,id):
        model.delete_info_from_table("kh_material", id)
        raise web.seeother("/material")

# 删除类别信息
class DeleteCategory:
    def POST(self, id):
        model.delete_info_from_table("material_category", id)
        raise web.seeother("/materialCategory")

# 删除项目信息
class DeleteProject:
    def GET(self):
        return render.index(0)
    def POST(self, id):
        model.delete_info_from_table("kh_project", id)
        raise web.seeother("/project")

# 删除入库记录(根据唯一id号找到入库日志表中，并将status改为-1【已删除】)
class DeleteInStorageLog:
    def POST(self,id):
        model.delete_in_storage_log(id)
        raise web.seeother("/inStorageLog")



# 库存信息
class StorageInfo:
    def GET(self):
        allCategory = db.select("material_category")

        first_category_id = 0
        materials = {}

        # 获取第一个类别id
        if allCategory:
            first_category_id = db.select("material_category")[0]['serial_no']

            # 获取第一个类别的所有商品信息
            materials = db.select("kh_material", where="category_id=$first_category_id", vars=locals())

        time.sleep(0.5)
        return render.StorageInfo(list(allCategory),list(materials))


# 入库信息
class InStorage:
    def GET(self):
        # 获取所有类别信息
        allCategory=db.select("material_category")

        first_category_id = 0
        materials = {}
        recentOperate = {}

        # 获取第一个类别id
        value=db.select("material_category")
        if value :
            first_category_id = value[0]['serial_no']

            # 获取第一个类别的所有商品信息
            materials=db.select("kh_material", where="category_id=$first_category_id", vars=locals())

        # 最近入库的十条操作记录
        recentOperate=db.select("material_in_storage_log", order="create_time DESC",limit=5, vars=locals())

        time.sleep(0.5)
        return render.InStorage(list(allCategory),list(materials),list(recentOperate))

    def POST(self):
        # 商品入库  1、如果库存有这个商品且价格一样的话，数量累加，但是之前的入库时间就乱了2、直接存库位里，能看到是啥时候入库的
        # 目前先选择第二种

        current_material = json.loads(web.data())

        name = current_material['materialName']

        status = storage.material_in_storage(current_material)

        result = {
            0: "存入异常，请联系后台人员！",
            1: "商品已入库！",
            -2: "入库信息录入时发生异常！",
            -3: "日志信息录入时发生异常！",
            -4: "商品表中未找到该信息！",
            -5: "更新商品表状态发生异常！"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value, ensure_ascii=False)


# 用于商品入库模块
# 根据类别id显示该类别下所有商品详情

class CategoryChange:
    def POST(self):

        data = json.loads(web.data())
        category_id=data["category"]
        material = db.select("kh_material", where="category_id=$category_id", vars=locals())
        value = list(material)

        result={}
        result['msg'] = 'SUCCESS'
        result['material'] = value
        result['material_number'] = len(value)

        return json.dumps(result)

# 用于商品入库模块
# 根据类别名称显示该类别下所有商品详情

class CategoryNameChange:
    def POST(self):
        data = json.loads(web.data())
        category_name = data["category"]
        category_id = db.select("material_category", what='serial_no' , where="name=$category_name", vars=locals())[0]['serial_no']
        material = db.select("kh_material", where="category_id=$category_id", vars=locals())
        value = list(material)

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = value
        result['material_number'] = len(value)
        result['category_id'] = category_id

        return json.dumps(result)


# 用于入库模块 【已取消】
# 根据类别id和商品id，更新商品信息【名称、单位】
class MaterialChange:
    def POST(self):
        data = json.loads(web.data())
        category_id = data["categoryId"]
        material_id = data["materialId"]
        material = db.select("kh_material", where="category_id=$category_id AND material_id=$material_id", vars=locals())
        value = list(material)

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = value
        result['material_number'] = len(value)

        return json.dumps(result)


# 用于入库模块
# 根据类别id和商品id，更新商品信息【名称、单位】
class MaterialNameChange:
    def POST(self):
        data = json.loads(web.data())
        category_id = data["categoryId"]
        material_name = data["materialName"]
        #material_id = db.select("kh_material", what='material_id' , where="name=$material_name", vars=locals())[0]['material_id']
        material = db.select("kh_material", where="category_id=$category_id AND name=$material_name",
                             vars=locals())
        value = list(material)

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = value
        result['material_number'] = len(value)

        return json.dumps(result)


# 用于新增商品
# 根据类别id显示类别名称
class TypeChange:
    def POST(self):

        data = json.loads(web.data())
        category_id=data["category"]
        category_info = db.select("material_category", where="serial_no=$category_id", vars=locals())
        value = list(category_info)

        result={}
        result['msg'] = 'SUCCESS'
        result['category'] = value
        result['category_number'] = len(value)

        return json.dumps(result)


# 出库信息
class OutStorage:
    def GET(self):
        # 获取所有类别信息
        allCategory = db.select("material_category")

        first_category_id = 0
        materials = {}

        # 获取第一个类别id
        value = db.select("material_category")
        if value:
            first_category_id = value[0]['serial_no']

            # 获取第一个类别的所有商品信息
            materials = db.select("kh_material", where="category_id=$first_category_id", vars=locals())

        # 获取项目列表信息
        projects = model.select_table_from_sql("kh_project")

        time.sleep(0.5)
        return render.OutStorage(list(allCategory), list(materials), list(projects))

    def POST(self):
        # 存入material_io_storage_info库存信息表
        current_category = json.loads(web.data())

        # 该id为io库存表的中唯一id，非商品id
        id = current_category['id']
        outCount = current_category['outCount']

        status=storage.material_out_storage(current_category)

        result = {
            0: "存入异常，请联系后台人员！",
            1: "商品已出库！",
            -1: "库存表中未找到该信息！",
            -2: "更新库存信息失败！",
            -4: "日志信息录入时发生异常！",
            -5: "更新项目信息异常！！"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value, ensure_ascii=False)

# 出库条件筛选
class FilterMaterial:
    def POST(seif):
        data = json.loads(web.data())
        category_id = data["categoryId"]
        material_id = data["materialId"]

        # 从库存中筛选出来的信息
        material = db.select("material_io_storage_info", where="category_id=$category_id AND material_id=$material_id AND count>0",
                             vars=locals())
        filterMaterial = list(material)
        filterMaterial_number = len(filterMaterial)

        value = model.select_table_from_sql("kh_project")
        projects = list(value)

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = filterMaterial
        result['material_number'] = len(filterMaterial)

        return json.dumps(result,cls=ComplexEncoder)


# 库存信息条件筛选
class SearchMaterial:
    def POST(seif):
        data = json.loads(web.data())
        category_id = data["categoryId"]
        material_id = data["materialId"]
        storage_name = data["storageName"]

        # 从库存中筛选出来的信息
        if(storage_name == "全部"):
            material = db.select("material_io_storage_info",
                                 where="category_id=$category_id AND material_id=$material_id AND count>0",vars=locals())
        else:
            material = db.select("material_io_storage_info",
                                 where="category_id=$category_id AND material_id=$material_id AND count>0 AND storage_name=$storage_name",
                                 vars=locals())
        searchMaterial = list(material)
        searchMaterial_number = len(searchMaterial)

        totalCount = 0
        totalPrice = 0  # 总价计算【区分专普票】
        for i in range(0,searchMaterial_number):
            # 专票不含税
            if(searchMaterial[i]['invoice_type']=="专票"):
                value = searchMaterial[i]['price'] * int(searchMaterial[i]['count'])
            else:
                value = searchMaterial[i]['tax_price']

            totalPrice = totalPrice + value

            value = searchMaterial[i]['count']
            totalCount = totalCount + value
        totalPrice = format(totalPrice, '.6f')

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = searchMaterial
        result['total_price'] = totalPrice
        result['material_number'] = searchMaterial_number
        result['total_count'] = totalCount

        return json.dumps(result,cls=ComplexEncoder)

# 入库日志模块
class InStorageLog:
    def GET(self):
        logs = db.select("material_in_storage_log")
        time.sleep(0.5)
        return render.InStorageLog(list(logs))

# 出库日志模块
class OutStorageLog:
    def GET(self):
        logs = db.select("material_out_storage_log")
        time.sleep(0.5)
        return render.OutStorageLog(list(logs))

class Index:
    def GET(self):
        return render.index(0)

# 导出信息
class StorageLogExport:
    def POST(self):
        data = json.loads(web.data())
        # 入库日志
        if(data['type']=="in"):
            status = storage.export_in_storage_log(data)
        # 出库日志
        elif (data['type'] == "out"):
            status = storage.export_out_storage_log(data)

        result=""
        if(status==1):
            result = "日志已生成成功！请到文件夹下查看！"
        elif (status==-1):
            result = "未查询到操作！生成失败！"
        return json.dumps(result, cls=ComplexEncoder)

# 日志筛选
class StorageLogfilter:
    def POST(self):
        data = json.loads(web.data())
        # 入库日志筛选
        if (data['type'] == "in"):
            log = storage.filter_in_storage_log(data)
        # 出库日志筛选
        elif (data['type'] == "out"):
            log = storage.filter_out_storage_log(data)

        result = {}

        result['msg'] = 'SUCCESS'
        result['filter_log'] = log

        return json.dumps(result, cls=ComplexEncoder)

# 借贷还货功能
class MaterialBorrow:
    def GET(self):
        # 申领仓库和实际出货仓库不一致的，即为跨库出货
        table="material_out_storage_log"
        borrowLogs = list(db.select(table,where="apply_storage!=storage_name AND status='borrow'",vars=locals()))
        return render.MaterialBorrow(borrowLogs)

    def POST(self):
        data = json.loads(web.data())

        status = storage.material_returned_info(data)

        result = {
            0:  "借调功能：更新借调日志时出借，请联系后台人员！",
            1:  "借调功能：还货成功！",
            -1: "借调功能：库存增加出错，请联系后台人员！",
            -2: "借调功能：库存减少出错，请联系后台人员！",
            -3: "借调功能：更新出库日志出错！",
            -4: "借调功能：更新入库记录标志位出错！"
        }

        value = result.get(status, None)

        return json.dumps("提示：" + value, ensure_ascii=False)

# 根据欠货的那条日志，来找到符合还货的库存信息
class StockInfo:
    def POST(self):
        info = json.loads(web.data())
        material = storage.filter_stock_borrow_info(info)

        result = {}

        result['stock_info'] = material

        return json.dumps(result, cls=ComplexEncoder)


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
    # now = datetime.date.today()
    # a = firstDayOfMonth(now)