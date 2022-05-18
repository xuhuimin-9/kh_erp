#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from datetime import date, datetime
from decimal import Decimal

import web
import json
import time
import model
import storage
import json

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

    "/storageInfo", "StorageInfo",
    "/inStorage", "InStorage",
    "/outStorage", "OutStorage",

    "/categoryChange", "CategoryChange",
    "/categoryNameChange", "CategoryNameChange",

    "/materialChange", "MaterialChange",
    "/materialNameChange", "MaterialNameChange",

    "/filterMaterial", "FilterMaterial",
    "/searchMaterial" , "SearchMaterial",
    "/typeChange", "TypeChange"


)


t_globals = {"datestr": web.datestr}
render = web.template.render("templates", base="base", globals=t_globals)

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
        return render.MaterialCategory(material_category)

    def POST(self):
        new_material_category = web.input()
        print(new_material_category)
        print(new_material_category['name'])
        print(new_material_category['number'])
        name = new_material_category['name']
        number = new_material_category['number']
        model.insert_info_to_material_category(name, number)

# 获取商品信息 和 新建商品信息
class Material:
    def GET(self):
        category = model.select_table_from_sql("material_category")
        material = model.select_table_from_sql("kh_material")
        time.sleep(0.5)
        return render.Material(category,material)

    def POST(self):
        new_material = web.input()
        print(new_material)
        category_name = new_material['category_name']
        category_id = db.select("material_category", what='serial_no' , where="name=$category_name", vars=locals())[0]['serial_no']
        material_id = new_material['material_id']
        print(type(material_id))
        material_id = int(float(material_id))
        material_id
        name = new_material['name']
        unit = new_material['unit']
        model.insert_info_to_kh_material(category_id, category_name,material_id, name, unit)

        # 同步存到库存信息中
        #storage.insert_info_to_material_io_storage_info(category_id, material_id, name, unit)

# 获取项目信息 和 创建项目信息
class Project:
    def GET(self):
        """ all project show """
        projects = model.select_table_from_sql("kh_project")
        time.sleep(0.5)
        return render.Project(projects)

    def POST(self):
        new_project = web.input()
        print(new_project)
        print(new_project['id'])
        print(new_project['name'])
        id = new_project['id']
        name = new_project['name']
        status = model.check_project_info(id,name)
        #model.insert_info_to_kh_project(id, name)
        if(status == 1):
            return json.dumps("提示：项目编号" + id + "重复！", ensure_ascii=False)
        if(status == 2):
            return json.dumps("提示：项目名称" + name + "重复！", ensure_ascii=False)

        return json.dumps("提示：项目" + name + "已添加！", ensure_ascii=False)


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
        """ all project show """
        #projects = model.select_table_from_sql("kh_project")
        return render.index(0)
    def POST(self, id):
        model.delete_info_from_table("kh_project", id)
        raise web.seeother("/project")

# 库存信息
class StorageInfo:
    def GET(self):
        materials = db.select("material_io_storage_info")
        allCategory = db.select("material_category")
        time.sleep(0.5)
        return render.StorageInfo(list(allCategory),list(materials))


# 入库信息
class InStorage:
    def GET(self):
        # 获取所有类别信息
        allCategory=db.select("material_category")
        print(allCategory)

        first_category_id = 0
        materials = {}

        # 获取第一个类别id
        value=db.select("material_category")
        if value :
            first_category_id = value[0]['serial_no']
            # first_category_id=db.select("material_category")[0]['serial_no']
            first_category_id=int(first_category_id)

            # 获取第一个类别的所有商品信息
            materials=db.select("kh_material", where="category_id=$first_category_id", vars=locals())

        time.sleep(0.5)
        return render.InStorage(list(allCategory),list(materials))

    def POST(self):
        # 商品入库  1、如果库存有这个商品且价格一样的话，数量累加，但是之前的入库时间就乱了2、直接存库位里，能看到是啥时候入库的
        # 目前先选择第二种

        # 存入material_io_storage_info库存信息表
        current_material = json.loads(web.data())
        print(current_material)

        # category_id = current_material['categoryId']
        # category_name = current_material['categoryName']
        # material_id = current_material['materialId']
        name = current_material['materialName']
        # unit = current_material['materialUnit']
        # count = current_material['materialCount']
        # price = current_material['materialPrice']
        # tax = current_material['materialTax']
        # tax_price = current_material['materialTaxPrice']

        #status = storage.material_in_storage(category_id, material_id, name, unit, count, price, tax,tax_price)

        status = storage.material_in_storage(current_material)

        if(status == 1):
            return json.dumps("提示：商品" + name + "已入库！", ensure_ascii=False)
        else :
            return json.dumps("提示：商品" + name + "入库异常！", ensure_ascii=False)

# 用于商品入库模块
# 根据类别id显示该类别下所有商品详情

class CategoryChange:
    def POST(self):

        data = json.loads(web.data())
        print(data)
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
        print(data)
        category_name = data["category"]
        category_id = db.select("material_category", what='serial_no' , where="name=$category_name", vars=locals())[0]['serial_no']
        material = db.select("kh_material", where="category_id=$category_id", vars=locals())
        value = list(material)

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = value
        result['material_number'] = len(value)

        return json.dumps(result)

# 用于入库模块 【已取消】
# 根据类别id和商品id，更新商品信息【名称、单位】

class MaterialChange:
    def POST(self):
        data = json.loads(web.data())
        print(data)
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
        print(data)
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
        print(data)
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
        # print(allCategory)

        first_category_id = 0
        materials = {}

        # 获取第一个类别id
        value = db.select("material_category")
        if value:
            first_category_id = value[0]['serial_no']
            # first_category_id=db.select("material_category")[0]['serial_no']
            first_category_id = int(first_category_id)

            # 获取第一个类别的所有商品信息
            materials = db.select("kh_material", where="category_id=$first_category_id", vars=locals())

        # 获取项目列表信息
        projects = model.select_table_from_sql("kh_project")

        time.sleep(0.5)
        return render.OutStorage(list(allCategory), list(materials),list(projects))

    def POST(self):
        # 存入material_io_storage_info库存信息表
        current_category = json.loads(web.data())
        print(current_category)

        # 该id为io库存表的中唯一id，非商品id
        id = current_category['id']
        outCount = current_category['outCount']

        storage.material_out_storage(current_category)

# 出库条件筛选
class FilterMaterial:
    def POST(seif):
        data = json.loads(web.data())
        print(data)
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
        print(data)
        category_id = data["categoryId"]
        material_id = data["materialId"]

        # 从库存中筛选出来的信息
        material = db.select("material_io_storage_info", where="category_id=$category_id AND material_id=$material_id AND count>0",
                             vars=locals())
        searchMaterial = list(material)
        searchMaterial_number = len(searchMaterial)

        totalCount = 0
        totalPrice = 0  # 含税总价计算
        for i in range(0,searchMaterial_number):
            value = searchMaterial[i]['tax_price']
            # totalPrice = float(Decimal(str(totalPrice + value))) # 不可行 累加会出现小数过多的情况
            totalPrice = totalPrice + value
            value = searchMaterial[i]['count']
            totalCount = totalCount + value
        totalPrice = format(totalPrice, '.2f')

        result = {}
        result['msg'] = 'SUCCESS'
        result['material'] = searchMaterial
        result['total_price'] = totalPrice
        result['material_number'] = searchMaterial_number
        result['total_count'] = totalCount

        return json.dumps(result,cls=ComplexEncoder)


class Index:
    def GET(self):
        """ all project show """
        #projects = model.select_table_from_sql("kh_project")
        return render.index(0)


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()