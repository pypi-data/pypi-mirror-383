from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends,HTTPException
from importlib.resources import files, as_file

import json
import os
import glob
from brave.api.config.config import get_settings
from brave.api.enum.component_script import ScriptName
from brave.api.service import namespace_service
from brave.api.service.pipeline import get_pipeline_dir,get_pipeline_list
from collections import defaultdict
from brave.api.models.core import t_pipeline_components,t_pipeline_components_relation,t_namespace
import uuid
from brave.api.config.db import get_engine
from sqlalchemy import or_, select, and_, join, func,insert,update
import re
from brave.api.schemas.pipeline import PagePipelineQuery, SavePipeline,Pipeline,QueryPipeline,QueryModule, SavePipelineComponentsEdges,SavePipelineRelation,SaveOrder
import brave.api.service.pipeline  as pipeline_service
from sqlalchemy import  Column, Integer, String, Text, select, cast, null,text,case
from sqlalchemy.orm import aliased
from sqlalchemy.sql import union_all
from brave.api.service.sse_service import SSESessionService
import brave.api.utils.service_utils  as service_utils
import asyncio
import time
from starlette.concurrency import run_in_threadpool
from typing import List
import brave.api.service.container_service as container_service
from brave.app_container import AppContainer
import brave.api.service.notebook as notebook_service
import shutil
from fastapi import  File, UploadFile
import shutil
import time


pipeline = APIRouter()

def camel_to_snake(name):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# pipeline,software,file,downstream
# BASE_DIR = os.path.dirname(__file__)
@pipeline.post("/import-pipeline",tags=['pipeline'])
async def import_pipeline():
    pipeline_files = get_pipeline_list()
    new_pipeline_components_list = [] 
    new_pipeline_components_relation_list = []
    with get_engine().begin() as conn:
        pipeline_list = find_db_pipeline(conn, "pipeline")
        db_pipeline_key_list = [item.install_key for item in pipeline_list ]
        for pipeline_item_file in pipeline_files:
            json_data = get_pipeine_content(pipeline_item_file)
            install_key = os.path.basename( os.path.dirname(pipeline_item_file))
            if install_key in db_pipeline_key_list:
                continue
            pipeline_item = {k:v for k,v in json_data.items() if  k !="items"}
            pipeline_components_id =install_key# str(uuid.uuid4())
            # pipeline_id  = pipeline_components_id
            new_pipeline_components_list.append({
                "component_id":pipeline_components_id,
                "install_key":install_key,
                # "pipeline_key":wrap_pipeline_key,
                # "parent_pipeline_id":"0",
                "component_type":"pipeline",
                "content":json.dumps(pipeline_item)
            })

            keys_to_remove = [ 'inputFile','outputFile']
            for analysis_software in json_data['items']:
                analysis_software_ = {k:v for k,v in analysis_software.items() if  k not in keys_to_remove}
                analysis_software_uuid = str(uuid.uuid4())
                new_pipeline_components_list.append({
                    "component_id":analysis_software_uuid,
                    "install_key":install_key,
                    # "parent_pipeline_id":wrap_pipeline_uuid,
                    # "pipeline_key":wrap_pipeline_key,
                    "component_type":"software",
                    "content":json.dumps(analysis_software_)
                })
                new_pipeline_components_relation_list.append({
                    "relation_type":"pipeline_software",
                    "install_key":install_key,
                    "component_id":analysis_software_uuid,
                    "parent_component_id":pipeline_components_id,
                    # "pipeline_id":pipeline_id
                })
                for key in keys_to_remove:
                    add_analysis_file( analysis_software_uuid,install_key,analysis_software,key,new_pipeline_components_list,new_pipeline_components_relation_list)
                # key= "parseAnalysisResultModule"
        insert_stmt = insert(t_pipeline_components).values(new_pipeline_components_list)
        conn.execute(insert_stmt)
        insert_stmt = insert(t_pipeline_components_relation).values(new_pipeline_components_relation_list)
        conn.execute(insert_stmt)
        return {
            "pipeline":new_pipeline_components_list,
            "relation_pipeline":new_pipeline_components_relation_list
        }
        

def add_analysis_file(analysis_software_uuid,install_key,pipeline_item,key,new_pipeline_components_list,new_pipeline_components_relation_list):
    if key in pipeline_item:
              
        for analysis_file in pipeline_item[key]:
            analysis_file_uuid = str(uuid.uuid4())  
            # if key=='downstreamAnalysis':
            analysis_file_ = {k:v for k,v in analysis_file.items() if  k !="downstreamAnalysis"}
            new_pipeline_components_list.append({
                "component_id":analysis_file_uuid,
                "install_key":install_key,
                # "parent_pipeline_id":pipeline_uuid,
                # "pipeline_key":wrap_pipeline_key,
                "component_type":"file",
                "content":json.dumps(analysis_file_)
            })
            if key=="inputFile":
                new_pipeline_components_relation_list.append({
                    "relation_type":"software_input_file",
                    "install_key":install_key,
                    "component_id":analysis_file_uuid,
                    # "pipeline_id":pipeline_id,
                    "parent_component_id":analysis_software_uuid
                }) 
            elif  key=="outputFile":
                new_pipeline_components_relation_list.append({
                    "relation_type":"software_output_file",
                    "install_key":install_key,
                    "component_id":analysis_file_uuid,
                    # "pipeline_id":pipeline_id,
                    "parent_component_id":analysis_software_uuid
                })
            if "downstreamAnalysis" in analysis_file:
                for downstream_analysis in analysis_file["downstreamAnalysis"]:
                    downstream_analysis_uuid = str(uuid.uuid4()) 
                    new_pipeline_components_list.append({
                        "component_id":downstream_analysis_uuid,
                        "install_key":install_key,
                        # "parent_pipeline_id":item_uuid,
                        # "pipeline_key":wrap_pipeline_key,
                        "component_type":"downstream",
                        "content":json.dumps(downstream_analysis)
                    })
                    new_pipeline_components_relation_list.append({
                        "relation_type":"file_script",
                        # "pipeline_id":pipeline_id,
                        "install_key":install_key,
                        "component_id":downstream_analysis_uuid,
                        "parent_component_id":analysis_file_uuid
                    })

            # else:
            # new_pipeline_list.append({
            #     "pipeline_id":item_uuid,
            #     "parent_pipeline_id":pipeline_uuid,
            #     "pipeline_key":wrap_pipeline_key,
            #     "pipeline_type":camel_to_snake(key),
            #     "content":json.dumps(item)
            # })

def find_db_pipeline(conn, component_type):
    return conn.execute(t_pipeline_components.select() 
        .where(t_pipeline_components.c.component_type==component_type)).fetchall()

@pipeline.get("/get-pipeline/{name}",tags=['pipeline'])
async def get_pipeline(name):
    pipeline_dir =  get_pipeline_dir()
    

    # filename = f"{name}.json"
    json_file = f"{pipeline_dir}/{name}/main.json"
    data = {
        # "files":json_file,
        # # "wrapAnalysisPipeline":name,
        # "exists":os.path.exists(json_file)
    }
    if os.path.exists(json_file):
        json_data = get_pipeine_content(json_file)
        data.update(json_data)
    return data

def get_pipeline_item(item):
    content= json.loads(item.content)
    return {
        "id":item.id,
        "pipeline_id":item.pipeline_id,
        "pipeline_key":item.pipeline_key,
        "parent_pipeline_id":item.parent_pipeline_id,
        "pipeline_order":item.pipeline_order,
        "pipeline_type":item.pipeline_type,
        **content
    }
@pipeline.get("/get-component-parent/{component_id}",tags=['pipeline'])
async def get_component_parent(component_id,component_type):
    

    base = select(
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.install_key,
        t_pipeline_components.c.content,
        t_pipeline_components.c.namespace,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.tags,
        t_namespace.c.name.label("namespace_name"),
        cast(null(), String(255)).label("relation_type"),
        cast(null(), String(255)).label("parent_component_id"),
        cast(null(), String(255)).label("order_index"),
        cast(null(), String(255)).label("relation_id"),
    ).select_from(
        t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    ).where(
        t_pipeline_components.c.component_id == component_id,
        t_pipeline_components.c.component_type == component_type,
    )

    tp1 = aliased(t_pipeline_components)
    tn1 = aliased(t_namespace)
    rel = t_pipeline_components_relation
    # fp = aliased(cte)  # 引用递归CTE自身
    # base_alias = base.alias()

    stmt_parenet = select(
        tp1.c.component_id,
        tp1.c.component_type,
        tp1.c.install_key,
        tp1.c.content,
        tp1.c.namespace,
        tp1.c.component_name,
        tp1.c.tags,
        tn1.c.name.label("namespace_name"),
        rel.c.relation_type,
        rel.c.parent_component_id,
        rel.c.order_index,
        rel.c.relation_id,
    ).select_from(
        tp1.outerjoin(tn1, tp1.c.namespace == tn1.c.namespace_id)
        .join(rel, tp1.c.component_id == rel.c.parent_component_id)
    ).where(
        rel.c.component_id == component_id
    )

    # # 合并 base 和 recursive，生成完整的递归CTE
    stmt = base.union_all(stmt_parenet) 
    with get_engine().begin() as conn:
        data = conn.execute(stmt).mappings().all()
    child_item  = next((item for item in data if item["component_type"] == component_type),None)
    if not child_item:
        raise HTTPException(status_code=500, detail=f"{component_id}没有找到!")  

    if component_type == "script":
        child_item = {
            **child_item,
            **json.loads(child_item["content"])
        }
        del child_item["content"]

    parent_item_list = [dict(item) for item in data if item['component_type'] != component_type]
    # resul_dict= {}
    # resul_dict['script'] = dict(child_item)
    child_item['parent'] = parent_item_list
    return child_item


@pipeline.get("/get-pipeline-dag/{pipeline_id}",tags=['pipeline'])
async def get_pipeline_dag(pipeline_id):
    s_alias = t_pipeline_components.alias("s")
    t_alias = t_pipeline_components.alias("t")
    stmt1 = (
        select(
            t_pipeline_components_relation.c.parent_component_id.label("source"),
            t_pipeline_components_relation.c.component_id.label("target"),
            s_alias.c.component_name.label("source_name"),
            t_alias.c.component_name.label("target_name"),
        )
        .select_from(
            t_pipeline_components_relation
            .join(s_alias, t_pipeline_components_relation.c.parent_component_id == s_alias.c.component_id)
            .join(t_alias, t_pipeline_components_relation.c.component_id == t_alias.c.component_id)
        )
        .where(
            and_(
                t_pipeline_components_relation.c.relation_type == "pipeline_software",
                t_pipeline_components_relation.c.pipeline_id == pipeline_id
            )
        )
    )
    stmt2 = (
        select(t_pipeline_components)
        .distinct()
        .select_from(
            t_pipeline_components_relation
            .join(
                t_pipeline_components,
                or_(
                    t_pipeline_components.c.component_id == t_pipeline_components_relation.c.parent_component_id,
                    t_pipeline_components.c.component_id == t_pipeline_components_relation.c.component_id
                )
            )
        )
        .where(
            and_(
                t_pipeline_components_relation.c.relation_type == "pipeline_software",
                t_pipeline_components_relation.c.pipeline_id == pipeline_id
            )
        )
    )
    stmt3 = select(t_pipeline_components).where(t_pipeline_components.c.component_id == pipeline_id)
    with get_engine().begin() as conn:
        data = conn.execute(stmt1).mappings().all()
        data2 = conn.execute(stmt2).mappings().all()
        data3 = conn.execute(stmt3).mappings().first()
    return {
        **data3,
        "edges":data,
        "nodes":data2
    }

@pipeline.get("/get-pipeline-v2/{name}",tags=['pipeline'])
async def get_pipeline_v2(name,component_type="pipeline"):
    with get_engine().begin() as conn:
        return pipeline_service.get_pipeline_v2(conn,name,component_type)


  
@pipeline.get("/get-component-module-content/{component_id}",tags=['pipeline'])
async def get_module_content(component_id,script_name:ScriptName):
    # module_dir = queryModule.component_id
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    # if queryModule.module_dir:
    #     module_dir = queryModule.module_dir
    module_info:dict = pipeline_service.find_component_module(find_component,script_name)
    # py_module_path = py_module['path']
    if module_info and os.path.exists(module_info['path']):
        with open(module_info['path'],"r") as f:
            module_content = f.read()
    # py_module['content'] = py_module_content
    return {
        "path":module_info['path'], 
        "content":module_content
    }
    

def get_pipeine_content(json_file):
    markdown_dict = get_all_markdown()
    with open(json_file,"r") as f:
        json_data = json.load(f)
        # update_downstream_markdown(json_data.items)
        for item1 in  json_data['items']:
            if "markdown" in item1:
                content = get_markdown_content(markdown_dict,item1['markdown'] )
                item1['markdown'] = content
            if "downstreamAnalysis" in item1:
                for item2 in item1['downstreamAnalysis']:
                    if "markdown" in item2:
                        content = get_markdown_content(markdown_dict,item2['markdown'] )
                        item2['markdown'] = content
    return json_data

def get_config():
    pipeline_dir =  get_pipeline_dir()
    config = f"{pipeline_dir}/config.json"
    if os.path.exists(config):
        with open(config,"r") as f:
            return json.load(f)
    else:
        return {}
    

def get_category(name,key):
    config = get_config()
    if "category" in config:
        category = config['category']
        if name in category:
            return category[name][key]
    return name

def get_pipeline_one_v2(item):
    try:
        data = json.loads(item.content)
        result = {
            "id":item.id,
            "component_id":item.component_id,
            "path":item.component_id,
            "name":data['name'],
            "category":data['category'],
            "img":f"/brave-api/img/{data['img']}",
            "tags":data['tags'],
            "description":data['description'] if 'description' in data else "",
            "order":item.order_index
        }
        return  result
    except (ValueError, TypeError):
        return {
            "id":item.id,
            "pipeline_id":item.component_id,
            "path":item.component_id,
            "name":"unkonw",
            "category":"unkonw",
            "img":f"/brave-api/img/unkonw",
            "tags":["unkonw"],
            "description":"unkonw",
            "order":item.order_index
        }       
@pipeline.get("/list-pipeline-v2",tags=['pipeline'])
async def list_pipeline_v2():
    with get_engine().begin() as conn:
        wrap_pipeline_list = find_db_pipeline(conn, "pipeline")
        pipeline_list = [get_pipeline_one_v2(item) for item in wrap_pipeline_list]
        # pipeline_list = sorted(pipeline_list, key=lambda x:x["order"] if x["order"] is not None else x["id"])
    
    grouped = defaultdict(list)
    for item in pipeline_list:
        grouped[item["category"]].append(item)

    result = []
    for category, items in grouped.items():
        result.append({
            "name": get_category(category,"name"),
            "items": items
        })
    return result
    # pass

def get_pipeline_one(item):
    with open(item,"r") as f:
        data = json.load(f)
    data = {
        "path":os.path.basename(os.path.dirname(item)),
        "name":data['name'],
        "category":data['category'],
        "img":f"/brave-api/img/{data['img']}",
        "tags":data['tags'],
        "description":data['description'],
        "order":data['order']
    }
    return data

# @pipeline.get("/list-pipeline",tags=['pipeline'])
# async def get_pipeline():
#     # json_file = str(files("brave.pipeline.config").joinpath("config.json"))
#     # with open(json_file,"r") as f:
#     #     config = json.load(f)
#     # pipeline_files = files("brave.pipeline")
#     pipeline_files = get_pipeline_list()
#     pipeline_files = [get_pipeline_one(str(item)) for item in pipeline_files]
#     pipeline_files = sorted(pipeline_files, key=lambda x: x["order"])
#     grouped = defaultdict(list)
#     for item in pipeline_files:
#         grouped[item["category"]].append(item)

#     result = []
#     for category, items in grouped.items():
#         result.append({
#             "name": get_category(category,"name"),
#             "items": items
#         })
#     return result


def get_pipeline_file(filename):
    nextflow_dict = get_all_pipeline()
    if filename not in nextflow_dict:
        raise HTTPException(status_code=500, detail=f"{filename}不存在!")  
    return nextflow_dict[filename]

def get_all_pipeline():
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/*/nextflow/*.nf")
    nextflow_dict = {os.path.basename(item).replace(".nf",""):item for item in nextflow_list}
    return nextflow_dict



def get_all_markdown():
    pipeline_dir =  get_pipeline_dir()
    markdown_list = glob.glob(f"{pipeline_dir}/*/markdown/*.md")
    markdown_dict = {os.path.basename(item).replace(".md",""):item for item in markdown_list}
    return markdown_dict

def get_markdown_content(markdown_dict,name):
    markdown_file = markdown_dict[name]
    with open(markdown_file,"r") as f:
        content = f.read()
    return content

def get_downstream_analysis(item):
    with open(item,"r") as f:
        data = json.load(f)
    file_list = [
        item
        for d in data['items']
        if "downstreamAnalysis" in d
        for item in d['downstreamAnalysis']
    ]

    return file_list

@pipeline.get("/find_downstream_analysis/{analysis_method}",tags=['pipeline'])
async def get_downstream_analysis_list(analysis_method):
    pipeline_files = get_pipeline_list()
    downstream_list = [get_downstream_analysis(item) for item in pipeline_files]
    downstream_list = [item for sublist in downstream_list for item in sublist]
    downstream_dict = {item['saveAnalysisMethod']: item for item in downstream_list  if 'saveAnalysisMethod' in item}
    return downstream_dict[analysis_method]
    
@pipeline.post("/find-pipeline",tags=['pipeline'])
async def find_pipeline_by_id(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.find_pipeline_by_id(conn,queryPipeline.component_id)

@pipeline.post("/list-pipeline-components",tags=['pipeline'],response_model=list[Pipeline])
async def list_pipeline(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.list_pipeline(conn,queryPipeline)

@pipeline.post("/page-pipeline-components",tags=['pipeline'])
async def page_pipeline(query:PagePipelineQuery ):
    with get_engine().begin() as conn:
        return pipeline_service.page_pipeline(conn,query)


@pipeline.post("/save-pipeline-components-edges",tags=['pipeline'])
async def save_pipeline_components_edges(savePipelineComponentsEdges:SavePipelineComponentsEdges):
    with get_engine().begin() as conn:
        pipeline_service.save_pipeline_components_edges(conn,savePipelineComponentsEdges)
    return {"message":"success"}    

# def get_pipeline_id_by_parent_id(conn, start_id: str) -> str | None:
#     sql = text("""
#         WITH RECURSIVE ancestor_path AS (
#             SELECT
#                 pipeline_id,
#                 parent_pipeline_id,
#                 relation_type
#             FROM relation_pipeline
#             WHERE pipeline_id = :start_id

#             UNION ALL

#             SELECT
#                 rp.pipeline_id,
#                 rp.parent_pipeline_id,
#                 rp.relation_type
#             FROM relation_pipeline rp
#             JOIN ancestor_path ap ON rp.pipeline_id = ap.parent_pipeline_id
#         )
#         SELECT pipeline_id
#         FROM ancestor_path
#         WHERE relation_type = 'pipeline_software'
#         LIMIT 1;
#     """)

#     result = conn.execute(sql, {"start_id": start_id})
#     row = result.first()
#     return row[0] if row else None

@pipeline.post("/find-pipeline-relation/{relation_id}",tags=['pipeline'])
async def find_pipeline_relation(relation_id):
    with get_engine().begin() as conn:    
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
        return conn.execute(stmt).mappings().first()


@pipeline.post("/save-pipeline-relation",tags=['pipeline'])
async def save_pipeline_relation_controller(savePipelineRelation:SavePipelineRelation):
    with get_engine().begin() as conn:  
        await save_pipeline_relation(conn,savePipelineRelation)

        
        return {"message":"success"}

async def save_pipeline_relation(conn,savePipelineRelation):
    save_pipeline_relation_dict = savePipelineRelation.dict()
    # save_pipeline_relation_dict = {k:v for k,v in save_pipeline_relation_dict.items() if k!="pipeline_id"}
    if savePipelineRelation.parent_component_id:
        parent_component = pipeline_service.find_pipeline_by_id(conn,savePipelineRelation.parent_component_id)
        if parent_component:
            save_pipeline_relation_dict['namespace'] = parent_component["namespace"]
            namespace = parent_component["namespace"]
    if savePipelineRelation.relation_id:
        stmt = t_pipeline_components_relation.update().values(save_pipeline_relation_dict).where(t_pipeline_components_relation.c.relation_id==savePipelineRelation.relation_id)
    else:
        save_pipeline_relation_dict['relation_id'] = str(uuid.uuid4())
        child_component_count = pipeline_service.get_child_component_count(conn,namespace,savePipelineRelation.parent_component_id,savePipelineRelation.relation_type)
        save_pipeline_relation_dict['order_index'] = child_component_count + 1
        stmt = t_pipeline_components_relation.insert().values(save_pipeline_relation_dict)
        conn.execute(stmt)
    
    pipeline_service.write_all_component_relation(conn,namespace)

    # stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==savePipelineRelation.component_id)
    # find_pipeine = conn.execute(stmt).fetchone()
    # await run_in_threadpool(create_pipeline_dir, savePipelineRelation.pipeline_id, find_pipeine.content ,find_pipeine.component_type)
    # pipeline_service.create_wrap_pipeline_dir(savePipelineRelation.pipeline_id)
    # pipeline_service.create_file(savePipelineRelation.pipeline_id, find_pipeine.component_type,content)
    # content = json.loads(find_pipeine.content)



@pipeline.post("/save-pipeline",tags=['pipeline'])
async def save_pipeline(savePipeline:SavePipeline):
    
 
    save_pipeline_dict = savePipeline.dict()
    save_pipeline_dict = {k:v for k,v in save_pipeline_dict.items() if k!="parent_component_id" and k!="pipeline_id" and k!='relation_type' }
    
    with get_engine().begin() as conn:
        find_pipeine = None
        if savePipeline.component_id:
            stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id == savePipeline.component_id)
            find_pipeine = conn.execute(stmt).fetchone()

            if not find_pipeine:
                raise HTTPException(status_code=500, detail=f"根据{savePipeline.component_id}不能找到记录!")
            component_id = find_pipeine.component_id
            component_type = find_pipeine.component_type
        if find_pipeine:
            namespace = find_pipeine.namespace
            save_pipeline_dict = {k:v for k,v in save_pipeline_dict.items() if k!="component_id" and v is not  None and k!="namespace"} 
            stmt = t_pipeline_components.update().values(save_pipeline_dict).where(t_pipeline_components.c.component_id==savePipeline.component_id)
            conn.execute(stmt)
            
        # else:
        #     raise HTTPException(status_code=500, detail=f"根据{savePipeline.component_id}不能找到记录!")
        if not find_pipeine:
            if savePipeline.parent_component_id:
                parent_component = pipeline_service.find_pipeline_by_id(conn,savePipeline.parent_component_id)
                if parent_component:
                    save_pipeline_dict['namespace'] = parent_component.namespace
                    namespace = parent_component.namespace
                else:
                    raise HTTPException(status_code=500, detail=f"根据父{savePipeline.parent_component_id}不能找到记录!")
            else:
                namespace = savePipeline.namespace
                if not savePipeline.namespace:
                    raise HTTPException(status_code=500, detail=f"namespace不能为空!")
            str_uuid = str(uuid.uuid4())  
            save_pipeline_dict['component_id'] = str_uuid
            component_id = str_uuid
            stmt = t_pipeline_components.insert().values(save_pipeline_dict)
            conn.execute(stmt)
            component_type = save_pipeline_dict['component_type']
            # if savePipeline.component_type=="pipeline":
            
            # else:
            if savePipeline.relation_type:
                await save_pipeline_relation(conn, SavePipelineRelation(
                    component_id=component_id,
                    parent_component_id= savePipeline.parent_component_id,
                    relation_type=savePipeline.relation_type,
                    # pipeline_id=savePipeline.pipeline_id
                ))
        # content = json.loads(save_pipeline_dict['content'])
        # if component_type == "software" or component_type =="script":
        #     if "script_type" in content:
        #         await run_in_threadpool(pipeline_service.create_file,namespace, component_id ,component_type,content['script_type'])
        pipeline_service.write_all_component(conn,namespace)
    
    # t0 = time.time()
    

    # await asyncio.sleep(0.5)
    # print("文件创建耗时", time.time() - t0)

    return {"message":"success"}


# def create_pipeline_dir(pipeline_id,content,component_type):
#     # pipeline_service.create_wrap_pipeline_dir(pipeline_id)
#     # content = json.loads(content)
#     pipeline_service.create_file(pipeline_id,component_type,content)


@pipeline.delete("/delete-pipeline-relation/{relation_id}")
async def delete_pipeline_relation(relation_id: str):
    with get_engine().begin() as conn:
        component_relation = pipeline_service.find_by_relation_id(conn,relation_id)
        if not component_relation:
            raise HTTPException(status_code=500, detail=f"根据{relation_id}不能找到记录!") 
        stmt = t_pipeline_components_relation.delete().where(t_pipeline_components_relation.c.relation_id == relation_id)
        conn.execute(stmt)
        pipeline_service.write_all_component_relation(conn,component_relation.namespace)
        return {"message":"success"}



@pipeline.delete("/delete-component/{component_id}")
async def delete_component(component_id: str):

    with get_engine().begin() as conn:
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.parent_component_id ==component_id)
        parent_find_pipeine = conn.execute(stmt).fetchone()
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.component_id ==component_id)
        child_find_pipeine = conn.execute(stmt).fetchall()

        if  parent_find_pipeine or child_find_pipeine:
            raise HTTPException(status_code=500, detail=f"不能删除存在关联!") 
        else:
            find_component = pipeline_service.find_component_by_id(conn,component_id)
            stmt = t_pipeline_components.delete().where(t_pipeline_components.c.component_id == component_id)
            conn.execute(stmt)
            pipeline_service.delete_wrap_pipeline_dir(component_id)

    with get_engine().begin() as conn:   
        pipeline_service.write_all_component(conn,find_component["namespace"])
        pipeline_service.write_all_component_relation(conn,find_component["namespace"])
    return {"message":"success"}

@pipeline.get("/find-by-component-id/{component_id}",tags=['pipeline'])
async def find_by_components_id(component_id):
    with get_engine().begin() as conn:
        stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id == component_id)
        return conn.execute(stmt).mappings().first()

    

@pipeline.post("/import-namespace-component",tags=['pipeline'])
async def import_namespace_component(namespace:str,force:bool=False):
    with get_engine().begin() as conn:
        pipeline_service.import_component(conn,namespace,force)
        pipeline_service.import_component_relation(conn,namespace,force)
        namespace_service.import_namespace(conn,namespace,force)
        container_service.import_container(conn,namespace,force)
    return {"message":"success"}

def get_namespace_by_file(file):
    with open(file,"r") as f:
        data = json.load(f)
    return {
        "namespace_id":data['namespace_id'],
        "name":data['name'],
    }


@pipeline.get("/list-namespace-file",tags=['pipeline'])
async def list_namespace_file():
    pipeline_dir = get_pipeline_dir()
    namespace_list = glob.glob(f"{pipeline_dir}/*/namespace.json")
    namespace_list = [get_namespace_by_file(item) for item in namespace_list]

    return namespace_list


@pipeline.get("/get-depend-component/{component_id}",tags=['pipeline'])
async def get_depend_component(component_id):
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if not find_component:
            raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
        namespace = find_component['namespace']
        child_depend_component = pipeline_service.get_child_depend_component(conn, namespace, component_id)
        parent_depend_component = pipeline_service.get_parent_depend_component(conn, namespace, component_id)
        return list(child_depend_component) + list(parent_depend_component)


@pipeline.post("/save-component-relation-order",tags=['pipeline'])
async def save_component_relation_order(saveOrder:list[SaveOrder]):
    with get_engine().begin() as conn:
        pipeline_service.save_order(conn,saveOrder)
    return {"message":"success"}


@pipeline.post("/update-component-description/{component_id}",tags=['pipeline'])
async def update_component_description(component_id,description ):
    with get_engine().begin() as conn:
        pipeline_service.update_component_description(conn,component_id,description)
    return {"message":"success"}





@pipeline.post("/component/convert-ipynb/{component_id}",tags=['pipeline'])
async def convert_ipynb(component_id):
    # module_dir = queryModule.component_id
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    module_info:dict = pipeline_service.find_component_module(find_component, ScriptName.main)
    script_path  = module_info['path']
    ipynb_path = os.path.dirname(script_path)
    ipynb_path = f"{ipynb_path}/main.ipynb"
    if os.path.exists(script_path) and os.path.exists(ipynb_path):
        shutil.copy(script_path, f"{script_path}.tmp")
        notebook_service.convert_notebook(ipynb_path, script_path)
        return "success"
    raise HTTPException(status_code=404, detail=f"{script_path}或{ipynb_path}不存在!")


# @analysis_api.post("/analysis/convert-ipynb/{analysis_id}")
# async def convert_ipynb(analysis_id):
#     with get_engine().begin() as conn:
#         find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
#     script_path  = find_analysis["pipeline_script"]
#     ipynb_path = os.path.dirname(script_path)
#     ipynb_path = f"{ipynb_path}/main.ipynb"
#     if os.path.exists(script_path) and os.path.exists(ipynb_path):
#         shutil.copy(script_path, f"{script_path}.tmp")
#         notebook_service.convert_notebook(ipynb_path, script_path)
#         return "success"
#     raise HTTPException(status_code=404, detail=f"{script_path}或{ipynb_path}不存在!")


@pipeline.post("/component/upload/{component_id}")
async def upload_image(component_id,file: UploadFile = File(...)):
    # 限制只能上传图片类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=404, detail=f"只允许上传图片文件!")
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    module_info:dict = pipeline_service.find_component_module(find_component, ScriptName.main)
    script_path  = module_info['path']
    file_path = os.path.dirname(script_path)
    name, ext = os.path.splitext(file.filename)

    # file_path = os.path.join(file_path, file.filename)
    filename = f"main{ext}"
    file_path = f"{file_path}/{filename}"

    # 保存文件到本地
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    settings = get_settings()
    url_suffix = file_path.replace(str(settings.PIPELINE_DIR),"")
    ts_str = str(int(time.time()))

    url = f"/brave-api/pipeline-dir{url_suffix}?v={ts_str}"
    return {"filename": filename, "url":url}
