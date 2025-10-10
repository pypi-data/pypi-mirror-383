from collections import defaultdict
import json
import os
import glob

from dependency_injector.wiring import Provide
from sqlalchemy.orm import aliased
from brave.api.config.config import get_settings
from pathlib import Path
import shutil
from fastapi import Depends, HTTPException
from brave.api.schemas.pipeline import PagePipelineQuery, SavePipeline,Pipeline,QueryPipeline,QueryModule,SaveOrder,SavePipelineComponentsEdges
from brave.api.config.db import get_engine
from brave.api.models.core import t_namespace, t_pipeline_components, t_pipeline_components_edges, t_pipeline_components_relation
import importlib.resources as resources
from sqlalchemy import delete, select, and_, join, func,insert,update,or_
from datetime import datetime
from brave.api.enum.component_script import ScriptName
from sqlalchemy import  Column, Integer, String, Text, select, cast, null,text,case
from .notebook import generate_notebook
import brave.api.service.container_service as container_service

def get_pipeline_dir():
    settings = get_settings()
    return settings.PIPELINE_DIR

def get_pipeline_list():
    pipeline_dir =  get_pipeline_dir()
    pipeline_files = glob.glob(f"{pipeline_dir}/*/main.json")
    return pipeline_files
def get_module_name(item):
    pipeline_dir =  get_pipeline_dir()
    item_module = item.replace(f"{pipeline_dir}/","").replace("/",".")
    item_module = Path(item_module).stem 
    return item_module
    # return {os.path.basename(item).replace(".py",""):item_module} 
    # f'reads-alignment-based-abundance-analysis.py_plot.{module_name}'

def find_component_module(component,script_name:ScriptName) -> dict:
    # content = json.loads(component['content'])
    if "script_type" not in component:
        raise HTTPException(status_code=500, detail=f"script_type not found!")
    if script_name == ScriptName.main:
        script_type = component['script_type']
        if script_type == "nextflow":
            file_type = "nf"
        elif script_type == "python":
            file_type = "py"
        elif script_type == "shell":
            file_type = "sh"
        elif script_type == "r":
            file_type = "R"
        elif script_type == "jupyter":
            file_type = "ipynb"
        else:
            raise HTTPException(status_code=500, detail=f"script_type {script_type} not found!")
    else:
        file_type = "py"
    module_info = find_module(component['namespace'],component['component_id'],script_name,file_type)
    if module_info:
        return module_info
    else:
        if script_name == ScriptName.main:
            create_file(component['namespace'],component['component_id'],component['component_type'],file_type)
            module_info = find_module(component['namespace'],component['component_id'],script_name,file_type)
            if not module_info:
                raise HTTPException(status_code=500, detail=f"组件{component.component_id}的{script_name.value}模块没有找到!")
            return module_info
        else:
            default_module = get_default_module(script_name)
            return default_module
        # else:
        #     raise HTTPException(status_code=500, detail=f"{script_name.value}没有找到默认模块!")
    # try:
    # except Exception as e:
    #     print(f"Component with id {component.component_id} not found or missing content.")
    #     module_path =  create_file(component.namespace,component.component_id,content,component.component_type,file_type)

    # return module_path




def find_module(namespace,module_dir,script_name:ScriptName,file_type):
    # if script_name == ScriptName.input_parse:
    # if not module_name:
    #     if  module_type == "script":
    #         module_name = "main"
    #     else:
    #         return get_default_module(module_type)

        # raise HTTPException(status_code=500, detail=f"模块名称不能为空!")
    # if module_name =="default":
       
    path_dict = get_all_module(namespace,file_type)
    # if module_name is None: 
    #     module_name = module_type
    if module_dir in path_dict:
        module_dict = path_dict[module_dir]
        if script_name.value in module_dict:
            module_info = module_dict[script_name.value]
            return module_info
    return None
        # return get_default_module(module_type)
        # raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}没有找到!")
    

    # if script_name.value not in py_module_dir:
    #     raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}/{script_name.value}没有找到!")

    
    # return py_module

def get_default_module(script_name:ScriptName):
    if script_name == ScriptName.input_parse:
        py_parse_analysis = resources.files("brave.parse").joinpath("py_parse_analysis.py")
        return {
            "module":"brave.parse.py_parse_analysis",
            "path":str(py_parse_analysis)
        }
    if script_name == ScriptName.output_parse:
        py_parse_analysis_result = resources.files("brave.parse").joinpath("py_parse_analysis_result.py")
        return {
            "module":"brave.parse.py_parse_analysis_result",
            "path":str(py_parse_analysis_result)
        }
    raise HTTPException(status_code=500, detail=f"{script_name.value}没有找到默认模块!")
def get_all_module(namespace,file_type):
    suffix = file_type
    # if module_type.startswith("py_"):
    #     suffix = "py"
    # else:
    #     suffix = "nf"
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/{namespace}/*/*/*.{suffix}")
    result = {}
    for item in nextflow_list:
        
        parts = item.split(os.sep)
        dir_name = parts[-2]
        filename = os.path.basename(item).replace(f".{suffix}","")
        if dir_name not in result:
                result[dir_name] = {}
        
        item_module = get_module_name(item)
        result[dir_name][filename] = {
            "module":item_module,
            "path":item
        }
    
  
    # nextflow_dict = {os.path.basename(item).replace(".py",""):get_module_name(item) for item in nextflow_list}
    return result

def delete_wrap_pipeline_dir(pipeline_key):
    pipeline_dir =  get_pipeline_dir()
    src  =f"{pipeline_dir}/{pipeline_key}"
    dst  =f"{pipeline_dir}/bin"
    if not os.path.exists(dst):
        os.makedirs(dst)
    if os.path.exists(src):
        shutil.move(src,dst)

# def create_wrap_pipeline_dir(pipeline_key):
#     pipeline_dir = get_pipeline_dir()
#     img = f"{pipeline_dir}/{pipeline_key}/img"
#     nextflow = f"{pipeline_dir}/{pipeline_key}/nextflow"
#     py_parse_analysis = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis"
#     py_parse_analysis_result = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis_result"
#     py_plot = f"{pipeline_dir}/{pipeline_key}/py_plot"
    # dir_list = [img, nextflow,py_parse_analysis,py_parse_analysis_result,py_plot]
    # for item in dir_list:
    #     if not os.path.exists(item):
    #         os.makedirs(item) 

def create_file(namespace,component_id,component_type,file_type):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"

    content_text = ""
    if file_type == "py":
        with resources.files("brave.templete").joinpath(f"py_plot.py").open("r") as f:
            content_text = f.read()
    elif file_type == "nf":
        with resources.files("brave.templete").joinpath("nextflow.nf").open("r") as f:
            content_text = f.read()
    elif file_type == "R":
        with resources.files("brave.templete").joinpath("py_plot.R").open("r") as f:
            content_text = f.read()
    # if component_type == "pipeline":
    analysis_file = f"{pipeline_dir}/{component_type}/{component_id}/main.{file_type}"
    if not os.path.exists(analysis_file):
        dir_ = os.path.dirname(analysis_file)
        if not os.path.exists(dir_):
            os.makedirs(dir_) 
        if file_type=="ipynb":
            generate_notebook(analysis_file)
        else:
            with open(analysis_file,"w") as f:
                f.write(content_text)
            ipynb_path = os.path.dirname(analysis_file)
            generate_notebook(f"{ipynb_path}/main.ipynb")
    
    return analysis_file
        # if not os.path.exists(parseAnalysisModule):
        #     with open(parseAnalysisModule,"w") as f:
        #         f.write("")

    # if component_type == "software":
    #     # parseAnalysisModule = f"{pipeline_dir}/software/{component_id}/main.py"
    #     analysisPipline = f"{pipeline_dir}/software/{component_id}/main.{file_type}"
    #     # dir_list = [parseAnalysisModule,analysisPipline]
    #     # for item in dir_list:
    #     dir_ = os.path.dirname(analysisPipline)
    #     if not os.path.exists(dir_):
    #         os.makedirs(dir_) 
        
    #     if not os.path.exists(analysisPipline):
  
    #         with open(analysisPipline,"w") as f:
    #             f.write(content_text)
    #     return analysisPipline
    #     # if not os.path.exists(parseAnalysisModule):
    #     #     with resources.files("brave.templete").joinpath("py_parse_analysis.py").open("r") as f:
    #     #         content_text = f.read()
    #     #     with open(parseAnalysisModule,"w") as f:
    #     #         f.write(content_text)
        
    #     # if "parseAnalysisResultModule" in  content:
    #     #     parseAnalysisResultModule = content['parseAnalysisResultModule']
    #     #     for item in parseAnalysisResultModule:
    #     #         item_file = f"{pipeline_dir}/software/{component_id}/{item['module']}.py"
    #     #         dir_ = os.path.dirname(item_file)
    #     #         if not os.path.exists(dir_):
    #     #             os.makedirs(dir_) 
    #     #         if not os.path.exists(item_file):
    #     #             with resources.files("brave.templete").joinpath("py_parse_analysis_result.py").open("r") as f:
    #     #                 content_text = f.read()
    #     #             with open(item_file,"w") as f:
    #     #                 f.write(content_text)

    # if component_type == "script":
   

    #     py_plot = f"{pipeline_dir}/script/{component_id}/main.{file_type}"
    #     py_plot_dir = os.path.dirname(py_plot)
    #     if not os.path.exists(py_plot):
    #         if not os.path.exists(py_plot_dir):
    #             os.makedirs(py_plot_dir)
  
    #         with open(py_plot,"w") as f:
    #             f.write(content_text)

    #     nb_file = f"{pipeline_dir}/script/{component_id}/main.ipynb"
    #     if not os.path.exists(nb_file):
    #         generate_notebook(nb_file)

    #     return py_plot
    # raise HTTPException(status_code=500, detail=f"component_type {component_type} not create file!")


def find_component_by_id(conn,component_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    find_pipeine = conn.execute(stmt).mappings().first()
    return find_pipeine

def find_pipeline_by_id(conn,component_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    find_component = conn.execute(stmt).mappings().first()
    
    # component_type = find_component["component_type"]
    if find_component:
        find_component = dict(find_component)
        if find_component["container_id"]:
            find_container = container_service.find_container_by_id(conn,find_component["container_id"])
            find_component['container'] = find_container
        if find_component["sub_container_id"]:
            find_container = container_service.find_container_by_id(conn,find_component["sub_container_id"])
            find_component['sub_container'] = find_container

    # if find_component and find_component["server_container_id"]:
    #     find_component = dict(find_component)
    #     find_container = container_service.find_container_by_id(conn,find_component["container_id"])
    #     find_component['container'] = find_container
        # find_component['container_name'] = find_container["name"]
    return find_component

def find_component_by_parent_id(conn,parent_id,relation_type=None):
    stmt = (
        select(
            t_pipeline_components_relation,  # 关系表所有字段
            t_pipeline_components  # 组件表所有字段
        )
        .select_from(
            t_pipeline_components_relation.outerjoin(
                t_pipeline_components,
                t_pipeline_components_relation.c.component_id == t_pipeline_components.c.component_id
            )
        )
        .where(t_pipeline_components_relation.c.parent_component_id == parent_id)
    )

    if relation_type is not None:
        stmt = stmt.where(t_pipeline_components_relation.c.relation_type == relation_type)

    result = conn.execute(stmt).mappings().all()
    return result



def list_pipeline(conn,queryPipeline:QueryPipeline):
    stmt = t_pipeline_components.select() 
  
    conditions = []
    if queryPipeline.component_type is not None:
        conditions.append(t_pipeline_components.c.component_type == queryPipeline.component_type)
    if queryPipeline.namespace is not None:
        conditions.append(t_pipeline_components.c.namespace == queryPipeline.namespace)
    # if analysisResultQuery.ids is not None:
    #     conditions.append(analysis_result.c.id.in_(analysisResultQuery.ids))
    # if analysisResultQuery.analysis_method is not None:
    #     conditions.append(analysis_result.c.analysis_method.in_(analysisResultQuery.analysis_method))
    # if analysisResultQuery.analysis_type is not None:
    #     conditions.append(analysis_result.c.analysis_type == analysisResultQuery.analysis_type)
    stmt= stmt.where(and_( *conditions))

    # stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_type ==queryPipeline.component_type)
    find_pipeine = conn.execute(stmt).fetchall()
    return find_pipeine

def format_pipeline_componnet_one(item):
    try:
        content = json.loads(item['content'])
        item = {**content,**{k:v for k,v in item.items() if k != 'content'}}
        if 'img' in item:
            if not item['img']:
                item['img'] = f"/brave-api/img/pipeline.jpg"
    except Exception as e:
        print("component json error",json.dumps(item,indent=4))
 
        # else:
        #     item['img'] = f"/brave-api/pipeline-dir/{item['namespace']}/{item['component_type']}/{item['component_id']}/{item['img']}"
    return item

def page_pipeline(conn,query:PagePipelineQuery):
    stmt =select(
        t_pipeline_components,
        t_namespace.c.name.label("namespace_name")
    ) 
    
    # Left join with t_namespace to get namespace name
    stmt = stmt.select_from(
       t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    )

    conditions = []
    if query.component_type is not None:
        conditions.append(t_pipeline_components.c.component_type == query.component_type)

    if query.keywords:
        keyword_pattern = f"%{query.keywords}%"
        conditions.append(
            or_(
                t_pipeline_components.c.component_name.ilike(keyword_pattern),
                t_pipeline_components.c.tags.ilike(keyword_pattern),
                t_pipeline_components.c.description.ilike(keyword_pattern)
            )
        )

    stmt = stmt.where(and_(*conditions))
    count_stmt = select(func.count()).select_from(t_pipeline_components).where(and_(*conditions))

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [dict(item) for item in find_pipeline]
    find_pipeline = [format_pipeline_componnet_one(item) for item in find_pipeline]

    total = conn.execute(count_stmt).scalar()
    return {
        "items": find_pipeline,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }


def write_all_component(conn,namespace):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.namespace == namespace)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [ {k:v for k,v in item.items() if k!="id"} for item in find_pipeline]
    with open(f"{pipeline_dir}/pipeline_component.json","w") as f:
        json.dump(find_pipeline,f)
     

def import_component(conn,namespace,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    with open(f"{pipeline_dir}/pipeline_component.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component = find_pipeline_by_id(conn,item['component_id'])
        if find_pipeline_component:
            if force:
                update_stmt = update(t_pipeline_components).where(t_pipeline_components.c.component_id == item['component_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components).values(item))    
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")

def write_all_component_relation(conn,namespace):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.namespace == namespace)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [ {k:v for k,v in item.items() if k!="id" and k!="created_at" and k!="updated_at"} for item in find_pipeline]
    with open(f"{pipeline_dir}/pipeline_component_relation.json","w") as f:
        json.dump(find_pipeline,f, default=datetime_converter)

def import_component_relation(conn,namespace,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    with open(f"{pipeline_dir}/pipeline_component_relation.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component_relation = find_by_relation_id(conn,item['relation_id'])
        if find_pipeline_component_relation:
            if force:
                update_stmt = update(t_pipeline_components_relation).where(t_pipeline_components_relation.c.relation_id == item['relation_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components_relation).values(item))   


def find_by_relation_id(conn,relation_id:str):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
    find_pipeline = conn.execute(stmt).mappings().first()
    return find_pipeline



def find_component_by_namespace(conn,namespace):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.namespace == namespace)
    return conn.execute(stmt).mappings().all()

def find_component_by_container_id(conn,container_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.container_id == container_id)
    return conn.execute(stmt).mappings().all()

def get_child_depend_component(conn,namespace, component_id):
    
    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.description,
        t_pipeline_components.c.namespace
        ).select_from(
            t_pipeline_components_relation.outerjoin(
                t_pipeline_components,
                t_pipeline_components_relation.c.component_id == t_pipeline_components.c.component_id,
            )
        ).where(
            t_pipeline_components_relation.c.parent_component_id == component_id,
            t_pipeline_components_relation.c.namespace == namespace
        )
    


    return conn.execute(stmt).mappings().all()

def get_parent_depend_component(conn, namespace, component_id):

    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,   
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.description,
        t_pipeline_components.c.namespace
    ).select_from(
        t_pipeline_components_relation.outerjoin(
            t_pipeline_components,
            t_pipeline_components_relation.c.parent_component_id == t_pipeline_components.c.component_id,
        )
    ).where(
        t_pipeline_components_relation.c.component_id == component_id,
        t_pipeline_components_relation.c.namespace == namespace
    )
    return conn.execute(stmt).mappings().all()




def get_child_component_count(conn,namespace, component_id,relation_type):
    stmt = select(func.count()).select_from(t_pipeline_components_relation).where(
        t_pipeline_components_relation.c.parent_component_id == component_id,
        t_pipeline_components_relation.c.relation_type == relation_type,
        t_pipeline_components_relation.c.namespace == namespace
    )
    return conn.execute(stmt).scalar()


def save_order(conn,saveOrderList:list[SaveOrder]):
    for saveOrder in saveOrderList:
        stmt = update(t_pipeline_components_relation).where(t_pipeline_components_relation.c.relation_id == saveOrder.relation_id).values(order_index=saveOrder.order_index)
        conn.execute(stmt)



def save_pipeline_components_edges(conn,savePipelineComponentsEdges:SavePipelineComponentsEdges):
    # stmt = delete(t_pipeline_components_edges).where(t_pipeline_components_edges.c.pipeline_id == savePipelineComponentsEdges.component_id)
    # conn.execute(stmt)
    # for pipeline_components_edge in savePipelineComponentsEdges.pipeline_components_edges:
    #     stmt = insert(t_pipeline_components_edges).values(
    #         source=pipeline_components_edge.source,
    #         sourceHandle=pipeline_components_edge.sourceHandle,
    #         target=pipeline_components_edge.target,
    #         targetHandle=pipeline_components_edge.targetHandle,
    #         pipeline_id=savePipelineComponentsEdges.component_id
    #     )
    #     conn.execute(stmt)
        
    update_stmt = update(t_pipeline_components).where(
        t_pipeline_components.c.component_id == savePipelineComponentsEdges.component_id
        ).values(position=savePipelineComponentsEdges.position,
        edges=savePipelineComponentsEdges.edges  )
    conn.execute(update_stmt)





def get_pipeline_v2(conn,name,component_type="pipeline"):
    base = (select(
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.install_key,
        t_pipeline_components.c.content,
        t_pipeline_components.c.namespace,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.position,
        t_pipeline_components.c.edges,
        t_pipeline_components.c.tags,
        t_pipeline_components.c.description,
        t_namespace.c.name.label("namespace_name"),
        cast(null(), String(255)).label("relation_type"),
        cast(null(), String(255)).label("parent_component_id"),
        cast(null(), String(255)).label("order_index"),
        cast(null(), String(255)).label("relation_id"),
    ).select_from(
        t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    ).where(
        t_pipeline_components.c.component_id == name,
        t_pipeline_components.c.component_type == component_type,
    ).cte(name="base", recursive=True))


    # 递归 CTE 定义
    # cte = base.cte(name="full_pipeline", recursive=True)

    tp1 = aliased(t_pipeline_components)
    tn1 = aliased(t_namespace)
    rel = t_pipeline_components_relation
    # fp = aliased(cte)  # 引用递归CTE自身
    base_alias = base.alias()

    recursive = select(
        tp1.c.component_id,
        tp1.c.component_type,
        tp1.c.install_key,
        tp1.c.content,
        tp1.c.namespace,
        tp1.c.component_name,
        tp1.c.position,
        tp1.c.tags,
        tp1.c.edges,
        tp1.c.description,
        tn1.c.name.label("namespace_name"),
        rel.c.relation_type,
        rel.c.parent_component_id,
        rel.c.order_index,
        rel.c.relation_id,
    ).select_from(
        tp1.outerjoin(tn1, tp1.c.namespace == tn1.c.namespace_id)
        .join(rel, tp1.c.component_id == rel.c.component_id)
        .join(base_alias, rel.c.parent_component_id == base_alias.c.component_id)
    )

    # # 合并 base 和 recursive，生成完整的递归CTE
    cte = base.union_all(recursive) #.cte(name="full_pipeline", recursive=True)

    # # 最终查询排序
    final_query = select(cte).order_by(
        case((cte.c.order_index == None, 1), else_=0),
        cte.c.order_index
        # func.coalesce(cte.c.order_index, cte.c.relation_id),
    )
    # 执行查询
    # with get_engine().begin() as conn:
    # [dict(item) for item in data]
    data = conn.execute(final_query).mappings().all()
    if  len(data) < 0:
        raise HTTPException(status_code=500, detail=f"{name}没有找到!")  
    id_to_node = {(item["component_id"], item["relation_type"]): get_one_data(item) for item in data}
    children_map = defaultdict(list)
    for item in data:
        parent_id = item.get("parent_component_id")
        if parent_id:
            # parent_key = (parent_id, item["relation_id"])  # parent 的唯一标识
            child_key = (item["component_id"], item["relation_type"])
            children_map[parent_id].append(child_key)
    # 获取根 pipeline_id
    root_item  = next((item for item in data if item["component_type"] == component_type),None)
    if not root_item:
        raise HTTPException(status_code=500, detail=f"{name}没有找到!")  
    # root_key = (root_item["component_id"], None)
    if component_type == "software":
        result = build_software_structure(id_to_node,children_map,root_item)
    elif component_type == "pipeline":
        result = build_pipeline_structure(id_to_node,children_map,root_item)
    elif component_type == "file":
        result = build_file_structure(id_to_node,children_map,root_item)
    else:
        raise HTTPException(status_code=500, detail=f"{component_type}没有结构解析!")  
    return result

def get_one_data(item):
    try:
        content = json.loads(item["content"])
    except Exception as e:
        print("component json error",json.dumps(dict(item),indent=4))
        print("component json error",e)
        content = {}
    # end try
    
    item = {k:v for k,v in item.items() if k!="content"}
    return { **content,**item }

def build_file_structure(id_to_node,children_map,root_item):
    
    item = {**root_item, "downstreamAnalysis": []}
    for ds_id in children_map.get(item["component_id"], []):
        downstream = id_to_node[ds_id]
        item["downstreamAnalysis"].append(downstream)
    return item

def  build_software_structure(id_to_node,children_map,root_item):
    # result = {**root_item}
    item = {**root_item}
    input_files = []
    output_files = []
    for sub_id in children_map.get(root_item["component_id"], []):
        sub = id_to_node[sub_id]
        sub_content = sub
        if sub["relation_type"] == "software_input_file":
            input_files.append(sub_content)
        elif sub["relation_type"] == "software_output_file":
            sub_out = {**sub_content, "downstreamAnalysis": []}
            for ds_id in children_map.get(sub["component_id"], []):
                downstream = id_to_node[ds_id]
                sub_out["downstreamAnalysis"].append(downstream)
            output_files.append(sub_out)    
    return {**item, "inputFile":input_files, "outputFile":output_files}

def build_pipeline_structure(id_to_node,children_map,root_item):
    # node = id_to_node[pid]
    result = {**root_item}
    items = []
    for child_id in children_map.get(root_item["component_id"], []):
        child = id_to_node[child_id]
        content = child
        if child["component_type"] == "software":
            item = {**content}
            input_files = []
            output_files = []
            for sub_id in children_map.get(child_id[0], []):
                sub = id_to_node[sub_id]
                sub_content = sub
                if sub["relation_type"] == "software_input_file":
                    input_files.append(sub_content)
                elif sub["relation_type"] == "software_output_file":
                    sub_out = {**sub_content, "downstreamAnalysis": []}
                    for ds_id in children_map.get(sub["component_id"], []):
                        downstream = id_to_node[ds_id]
                        sub_out["downstreamAnalysis"].append(downstream)
                    output_files.append(sub_out)


            if input_files:
                item["inputFile"] = input_files
            if output_files:
                item["outputFile"] = output_files
            if "upstreamFormJson" in content:
                item["upstreamFormJson"] = content["upstreamFormJson"]
            items.append(item)
    if items:
        # result["items"] = items
        # item["databases"] for item in items if "databases" in item
        result["databases"] = [
             db for item in items if "databases" in item for db in item["databases"]
        ]
        result["upstreamFormJson"] = [
            db for item in items if "upstreamFormJson" in item and isinstance(item["upstreamFormJson"],list) and len(item["upstreamFormJson"]) > 0   for db in item["upstreamFormJson"]
        ]
        result["software"] = items
        if items and len(items) > 0 and "inputFile" in items[0]:
            result["inputFile"] = items[0]["inputFile"]
        else:
            result["inputFile"] = []
    return result


  
def update_component_description(conn, component_id,description):
    stmt = t_pipeline_components.update().where(t_pipeline_components.c.component_id ==component_id).values(description=description)
    conn.execute(stmt)
    # pass