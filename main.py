#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import web
import json
import time
import model

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
    "/deleteProject/(\d+)" , "DeleteProject"
)


t_globals = {"datestr": web.datestr}
render = web.template.render("templates", base="base", globals=t_globals)

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
        model.insert_table_to_material_category(name, number)

# 获取商品信息 和 新建商品信息
class Material:
    def GET(self):
        material = model.select_table_from_sql("kh_material")
        time.sleep(0.5)
        return render.Material(material)

    def POST(self):
        new_material = web.input()
        print(new_material)
        category_id = new_material['category_id']
        material_id = new_material['material_id']
        name = new_material['name']
        unit = new_material['unit']
        model.insert_table_to_kh_material(category_id, material_id, name, unit)

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
        #model.insert_table_to_kh_project(id, name)
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

class Index:
    def GET(self):
        """ all project show """
        #projects = model.select_table_from_sql("kh_project")
        return render.index(0)


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()