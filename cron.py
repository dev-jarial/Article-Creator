# Fast API Lib
from fastapi import FastAPI, APIRouter, Depends,Request,HTTPException
from fastapi import Depends

# Router Lib
from app.api.api_v1.api import api_router
from app.core.config import settings

from app.api import deps
from sqlalchemy.orm import Session
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import delete,asc

import requests
import json
import tiktoken
# Cors Lib
from fastapi.middleware.cors import CORSMiddleware


import datetime

from app.db.session import SessionLocal
from app.models.prompts.process import Process
from app.models.prompts.prompt import Prompt
from app.models.prompts.article import Article
from app.models.prompts.setting import Setting

import openai
import time
from datetime import datetime


def find_item_id(item,section_id):
    if item['id'] == section_id:
        return item.get('length')

    if 'children' in item:
        for child in item['children']:
            result = find_item_id(child,section_id)
            if result:
                return result

    return None

def find_children_id(data_list, item_id):
    for item in data_list:
        if item['id'] == item_id:
            return item.get('length'),

        if 'children' in item:
            result = find_children_id(item['children'], item_id)
            if result:
                return result

    return None

# Define the request function
def make_request(process, session):
    try:
        prompt_data = session.query(Prompt).filter(Prompt.prompt_id == process.prompt_id).first()
        article_data =  session.query(Article).filter(Article.article_id == process.article_id).first()
        settings = session.query(Setting).filter(Setting.user_id == article_data.user_id).first()
        print('### open Key', settings.api_key)
        openai.api_key = settings.api_key

        section_id = process.section_id
        heading_data = article_data.heading_data

        for item in heading_data['data']:
            max_tokens = find_item_id(item,section_id)
            if max_tokens:
                break

        print("$$$$ lengt", process.prompt_id)
        print(type(process.prompt_id))
        
        if prompt_data:  
            response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                                {"role": "user", "content": process.prompt_format}
                            ]
                        )
            response = response["choices"][0]["message"]["content"]
            # print("working",response)
        else :    
            response = openai.Completion.create(
                model='text-ada-001',
                prompt=process.prompt_format,
                n=1,
                stop=None,
            )
            response = response.choices[0].text.strip()
        process.status = "completed"
        print("working"*10)
        print(response)
        #Todo for dynamic rate
        if prompt_data:  
            if prompt_data.gpt_model == "text-davinci-003":
                # cost of text-davinci-003
                training_rate = 0.0300
                usage_rate = 0.1200
            else:     
                # cost of text-ada-001
                training_rate = 0.0004
                usage_rate = 0.0016
        else:
            training_rate = 0.0004
            usage_rate = 0.0016            
                
        response_tokens = num_tokens_from_string(response, "gpt2")
   
        total_cost = calculate_cost(training_rate, usage_rate, response_tokens)
        # print('num_tokens #####',response_tokens)
        print('\n\ncurrent cost #####',total_cost)

        
        if article_data :
            cost = article_data.cost + total_cost
            article_data.cost = cost
            article_data.status = "active"
            total_words = article_data.total_words + len(response) if article_data.total_words is not None else len(response)
            article_data.total_words = total_words
            # print('Final cost in db ====>>>>>',article_data.cost)
            section_id = process.section_id
            data = article_data.heading_data
            print('Start ###',section_id)
            print('Response @@@',response)
            # print('Wait 10 sec')
            
            for item in data['data']:
                if item['id'] == section_id:
                    update_item(item,section_id,response)
                elif 'children' in item:
                    update_children(item['children'], section_id,response)

            process.response = response
            session.commit()

            articles =  session.query(Article).filter(Article.article_id == process.article_id).first()
            articles.heading_data = data
            session.commit()
        session.commit()


    except Exception as e:
        process.status = "pending"
        session.commit()
        print("Error!!")
        print(e)
        print("An exception occurred:", str(e))


def update_item(item, section_id, response):
    if item['id'] == section_id:
        item['is_completed'] = True
        item['response'] = response
    if 'children' in item:
        for child in item['children']:
            update_item(child, section_id, response)
            if child['id'] == section_id:
                return

def update_children(data_list, item_id, response):
    for item in data_list:
        if item['id'] == item_id:
            update_item(item, item_id, response)
        elif 'children' in item:
            update_children(item['children'], item_id, response)

# def update_item(item,response):
#     item['is_completed'] = True
#     item['response'] = response
#     if 'children' in item:
#         for child in item['children']:
#             update_item(child,response)

# def update_children(data_list, item_id,response):
#     for item in data_list:
#         if item['id'] == item_id:
#             update_item(item,response)
#         elif 'children' in item:
#             update_children(item['children'], item_id,response)



def num_tokens_from_string(string: str, encoding_name: str) -> int:
    # """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def calculate_cost(training_rate_per_1k, usage_rate_per_1k, num_tokens):

    # Calculate the cost per token
    training_cost_per_token = training_rate_per_1k / 1000
    usage_cost_per_token = usage_rate_per_1k / 1000

    # Calculate the total cost for the given number of tokens
    training_cost = num_tokens * training_cost_per_token
    usage_cost = num_tokens * usage_cost_per_token

    return training_cost + usage_cost

def process_openai_requests():

    session = SessionLocal()
    # As Open AI has limit of 3 request per minute
    pendingRequests = session.query(Process).filter(Process.status == "pending").order_by(asc(Process.created_at)).limit(50).all()
    
    if pendingRequests:
        for process in pendingRequests:
            # Change Pending to Progress
            process.status = "progress"
            session.commit()

            make_request(process, session)

    #delete completed record
    session.query(Process).filter(Process.status == "completed").delete()

    session.commit()
    session.close()


process_openai_requests()
