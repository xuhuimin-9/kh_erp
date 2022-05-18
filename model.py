import web, datetime
import time

db = web.database(dbn="mysql", db="kh_erp", host="localhost" , user="root" , password="123456")

def select_table_from_sql(table_name):
    return db.select(table_name,)


def insert_info_to_material_category(name, number):
    table_name = "material_category";
    db.insert(
        table_name, name = name , serial_no = number
    )

def insert_info_to_kh_material(category_id,category_name,material_id,name, unit):
    table_name = "kh_material";
    db.insert(
        table_name, category_id = category_id, category_name = category_name ,material_id = material_id ,name = name , unit = unit
    )

def insert_info_to_kh_project(project_id,name):

    table_name = "kh_project" ;
    db.insert(
        table_name, project_id = project_id, name = name
    )

def check_project_info(id,name):
    get_status = db.select("kh_project", where="project_id=$id", vars=locals())
    if(get_status):
        return 1   # id重复
    get_status = db.select("kh_project", where="name=$name", vars=locals())
    if(get_status):
        return 2    # 名称重复
    insert_info_to_kh_project(id, name)
    return 3    # 下发


def delete_info_from_table(table_name,id):
    db.delete(table_name, where="ID=$id", vars=locals())