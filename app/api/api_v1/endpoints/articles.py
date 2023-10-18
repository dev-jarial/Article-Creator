from fastapi import APIRouter, Depends, HTTPException
from app.schemas.prompts.article import ArticleCreate, ArticleUpdate
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.api import deps
from app.models.prompts.article import Article
from app.models.prompts.prompt import Prompt
from app.models.prompts.process import Process
from app.models.prompts.setting import Setting

from app.lib.utils.headers_scrapping import WebScraper, proxies
from app.lib.utils.related_searches import get_related_searches
from app.lib.utils.people_ask import get_google_results
from app.lib.utils.language_converter import translate_text
from fastapi.security.api_key import APIKey as SecureAPIKey
from app.lib.utils.api_tools import get_user, get_user_id
import people_also_ask
import people_also_ask.request.session
import hashlib
from datetime import datetime
from app.db.session import SessionLocal
import uuid
# from main import test
from googletrans import Translator
translator = Translator()


router = APIRouter()

# Get one by ID

@router.get("/{article_id}", tags=["articles"])
def get_article(article_id: str, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):

    user_id = get_user_id(db, api_key)

    query = db.query(Article)
    article = query.filter(Article.article_id == article_id).filter(
        Article.user_id == user_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
#Final step
@router.get("/{article_id}/finalStep", tags=["articles"])
def get_article(article_id: str, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):

    user_id = get_user_id(db, api_key)

    query = db.query(Article)
    article = query.filter(Article.article_id == article_id).filter(
        Article.user_id == user_id).first()

    data = article.heading_data
    
    # Extract all ids including children
    all_data = extract_data(data['data'])

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return all_data

def extract_data(data):
    new_data = []
    for item in data:
        current_id  = item['id']
        text        = item['text']
        response    = item['response']
        
        new_data.append({'id': current_id,'text' : text,'response':response})
        if 'children' in item and item['children']:
            children_data = extract_data(item['children'])
            new_data.extend(children_data)
    return new_data

# List

@router.get("/")
def get_article_list(db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user_id = get_user_id(db, api_key)
    articles = db.query(Article).filter(Article.user_id == user_id, Article.status == "active").order_by(desc(Article.created_at)).all()
    if not articles:
        raise HTTPException(status_code=404, detail="Articles not found")
    return articles


# Create

@router.post("/", status_code=200)
def create(article: ArticleCreate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user = get_user(db=db, api_key=api_key)

    # Create an instance of WebScraper with proxies
    scraper = WebScraper(proxies)

    # Scrape the headings from the article URLs
    scraper.scrape_headings(article.urls.split('\n'))

    # Extract the scraped headings
    headings = scraper.get_headings()

    suggested_h2s = []   # list for suggested_h2s
    
    # related_seaches call from lib.util ##################
    query1 = article.main_keywords
    language1 = article.language
    related_searches = get_related_searches(query1, language1)
    
    for related_search in related_searches:
        suggested_h2s.append(related_search)   
    # end of related_searches call ###########################
    
    #  from people aslo ask program
    query2 = article.main_keywords
    language2 = article.language
    also_suggested_h2s = get_google_results(query2, language2)
    
    # added both lists
    suggested_h2s+=also_suggested_h2s
    
        # If headings list is empty, add an H1 heading with the main keyword
    if not headings:
        heading_text = article.main_keywords
        heading_id = str(uuid.uuid4())  # Generate a unique ID

        headings.append({
            'text': heading_text,
            'level': 1,
            'id': heading_id,
            'children': [],
            'prompt_id': None,
            'response': '',
            'keywords': '',
            'expanded': True,
            'is_completed': False,
            'tag': 0,
            'more_info': '',
            'length': 500,
        })

    # print("------------------------")
    # print(suggested_h2s)
    
    # try:
    #     translator = Translator()

    #     if article.language.lower() == "polish":
    #         article.main_keywords = translator.translate(article.main_keywords, src='en', dest='pl').text
            
    #         # language convertion of heading. text key values
    #         data = headings
    #         translated_text = translate_text(data)
    #         # end of the convertion working functionality
                        
    #         for suggested_h2 in suggested_h2s:
    #             heading_text = suggested_h2.strip()
    #             heading_id = hashlib.sha1(heading_text.encode('utf-8')).hexdigest()
    #             translated_text = translator.translate(heading_text, src='en', dest='pl').text

    #             current_heading = {
    #                 'tag': 'h2',
    #                 'text': translated_text,
    #                 'level': 2,
    #                 'id': heading_id,
    #                 'children': [],
    #                 'prompt_id': None,
    #                 'response': '',
    #                 'keywords': ''
    #             }

    #             headings[0]['children'].append(current_heading)
    #     else:
            
    for suggested_h2 in suggested_h2s:
        heading_text = suggested_h2.strip()
        # heading_id = hashlib.sha1(heading_text.encode('utf-8')).hexdigest()
        heading_id = str(uuid.uuid4())  # Generate a unique ID
                
        current_heading = {
            'text': heading_text,
            'level': 2,
            'id': heading_id,
            'children': [],
            'prompt_id': None,
            'response': '',
            'keywords': '',
            'expanded': True,
            'is_completed': False,
            'tag': 1,
            'more_info': '',
            'length': 500,
        }
        if headings:
            headings[0]['children'].append(current_heading)
        else:
            pass    
    # except Exception as e:
    #     print(f"Translation error: {str(e)}")


    
    db_article = Article(
        language=article.language,
        main_keywords=article.main_keywords,
        urls=article.urls,
        status="draft",
        keywords=article.keywords,
        heading_data={
            'data': headings
        },
        created_at=datetime.now(),
        user=user
    )

    # Save the article to the database
    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    return db_article


# Update

@router.put("/{article_id}", status_code=200)
def update(article_id: str, article_update: ArticleUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    updated_article = update_article(article_id, article_update, db)
    # if URLs != New Ones  ---> Scraper

    return updated_article


def build_prompt_for_section(section_id, data, prompt_base, original_data):
    for item in data:
        if section_id == item["id"]:
            generate_value(item, prompt_base, original_data)
        if 'children' in item:
            build_prompt_for_section(section_id, item['children'], prompt_base, original_data)


#Regenerate
@router.post("/{article_id}/regenerate/{section_id}", status_code=200)
def regenerate(article_id: str,section_id: str ,data: ArticleUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):

    # Update
    user_id = get_user_id(db, api_key)
    settings = db.query(Setting).filter(Setting.user_id == user_id).first()
    if settings.api_key is None :
        raise HTTPException(status_code=404, detail="There is no OpenAI key found")
    article = update_article(article_id, data, db)

    heading_data = article.heading_data
    prompt_base = get_prompt_base(heading_data["data"], db)
    data = heading_data["data"]



    build_prompt_for_section(section_id, data, prompt_base, data)

    print("Updated Data")
    print(data)

    # Generate (Big Logic)
    # data = build_prompts(article, db)

    # TODO: Need to Find Good Solution
    article_session = SessionLocal()
    farticle = article_session.query(Article).filter(Article.article_id == article_id).first()
    farticle.heading_data  = {"data": data}
    article_session.commit()
    article_session.refresh(farticle)
    article_session.close()

    # Iterate Each Secion and Insert into new table for cron to handle
    process_list = scan_section_for_insertion(farticle.heading_data['data'], farticle)
    
    session = SessionLocal()

    for item in process_list:
        if item.section_id == section_id:
            # Check if a record with the same values already exists in the table
            existing_record = session.query(Process).filter_by(section_id=item.section_id, article_id=farticle.article_id).first()

            # If the record exists, update it; otherwise, add a new record
            if existing_record:
                # Update the existing record with the values from the dictionary
                for key, value in item.__dict__.items():
                    setattr(existing_record, key, value)
                # Regenerate The Status
                # TODO: Not resetting to regenerate
                setattr(existing_record, "status", "pending")
                session.commit()
            else:
                # Create a new instance of Process and add it to the session
                session.add(item)

    session.commit()
    session.close()


    farticle = db.query(Article).filter(Article.article_id == article_id).first()

    return farticle

    # End of Function
 
# Generate
@router.post("/{article_id}/generate", status_code=200)
def generate(article_id: str, data: ArticleUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    # Update
    # return {"data" : data}

    user_id = get_user_id(db, api_key)
    settings = db.query(Setting).filter(Setting.user_id == user_id).first()
    if data.is_meta:
        prompt = db.query(Prompt).filter(Prompt.prompt_id == settings.prompt_id).first()
        print("Type ####",type(data.heading_data["data"]))
        data.heading_data["data"].append(
            {
                "id": str(uuid.uuid4()),
                "tag" : "META DESCRIPTION",
                "text": "",
                "keywords": "",
                "prompt_id": prompt.prompt_id,
                "is_completed" : False
            }
        )

    if settings.api_key is None :
        raise HTTPException(status_code=404, detail="There is no OpenAI key found")
    article = update_article(article_id, data, db)

    # Generate (Big Logic)
    data = build_prompts(article, db)

    # TODO: Need to Find Good Solution
    article_session = SessionLocal()
    farticle = article_session.query(Article).filter(Article.article_id == article_id).first()
    farticle.heading_data  = {"data": data}
    article_session.commit()
    article_session.refresh(farticle)
    article_session.close()

    # Iterate Each Secion and Insert into new table for cron to handle
    process_list = scan_section_for_insertion(farticle.heading_data['data'], farticle)
    
    session = SessionLocal()

    for item in process_list:
        # Check if a record with the same values already exists in the table
        existing_record = session.query(Process).filter_by(section_id=item.section_id, article_id=farticle.article_id).first()

        # If the record exists, update it; otherwise, add a new record
        if existing_record:
            # Update the existing record with the values from the dictionary
            for key, value in item.__dict__.items():
                setattr(existing_record, key, value)
            # Regenerate The Status
            # TODO: Not resetting to regenerate
            setattr(existing_record, "status", "pending")
            session.commit()
        else:
            # Create a new instance of Process and add it to the session
            session.add(item)

    session.commit()
    session.close()


    farticle = db.query(Article).filter(Article.article_id == article_id).first()

    return farticle


# # Regenerate the section

# @router.post("/{article_id}/regenerate", status_code=200)
# def regenerate( section_id: str, data: ArticleUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    
#     user_id = get_user_id(db, api_key)
    
#     settings = db.query(Setting).filter(Setting.user_id == user_id).first()

#     if settings.api_key is None :
#         raise HTTPException(status_code=404, detail="There is no OpenAI key found")
    
#     process = Process(
#         # article_id = data.article_id,
#         keywords = data.keywords,
#         more_info = data.more_info,
#         prompt_id = data.prompt_id,
#         status = "pending",
#         created_at = datetime.now(),
#         # section_id = data.section_id
#     )
#     db.add(process)
#     db.commit()
#     db.refresh(process)

# @router.post("/{article_id}/regenerate/{section_id}", status_code=200)
# def regenerate_section(
#     article_id: str,
#     section_id: str,
#     prompts_id: str,  # New parameter to accept a list of prompt_ids
#     keywords: str,         # New parameter to accept keywords
#     more_info: str,        # New parameter to accept more info
#     db: Session = Depends(deps.get_db),
#     api_key: SecureAPIKey = Depends(deps.get_api_key)
# ):
#     # Get the user_id using the provided API key
#     user_id = get_user_id(db, api_key)

#     # Check if the article exists and belongs to the authenticated user
#     article = db.query(Article).filter(Article.article_id == article_id).filter(
#         Article.user_id == user_id).first()

#     if not article:
#         raise HTTPException(status_code=404, detail="Article not found")

#     # Find the specified section by its ID
#     section_to_regenerate = find_section_by_id(article.heading_data['data'], section_id)

#     if not section_to_regenerate:
#         raise HTTPException(status_code=404, detail="Section not found")

#     # Update the section with new data
#     section_to_regenerate['prompt_id'] = prompts_id
#     section_to_regenerate['keywords'] = keywords
#     section_to_regenerate['more_info'] = more_info
    
#     # Regenerate the section (Logic to regenerate the section)

#     # Save the regenerated section into the process_tbl
#     process = prepare_process(section_to_regenerate, article)

#     # Save the process record in the database
#     db.add(process)
#     db.commit()
#     db.refresh(process)

#     return process

# def find_section_by_id(data, section_id):
#     for item in data:
#         if item.get("id") == section_id:
#             return item
#         if 'children' in item:
#             section = find_section_by_id(item['children'], section_id)
#             if section:
#                 return section
#     return None


# Insert data to Process Table
def prepare_process(item, article):
    # print('###',item.get("prompt_id"))
    process = Process(
            section_id = item.get("id"),
            prompt_format = item.get("prompt_parsed_text"),
            prompt_id = item.get("prompt_id"),
            article = article,
            article_id = article.article_id,
            created_at = datetime.now(),
    )
    # print('$#$#@$ promt',process)
    return process


# TODO: Build for Insertion
def scan_section_for_insertion(data, article):
    process_list = []  # Empty list to store processes
    for item in data:
        process = prepare_process(item, article)
        process_list.append(process)
        if 'children' in item:
            child_processes = scan_section_for_insertion(item['children'], article)
            process_list.extend(child_processes)
    
    return process_list

    

# Delete
@router.delete("/{article_id}", status_code=204)
def delete(article_id: str, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user_id = get_user_id(db, api_key)
    article = db.query(Article).filter(Article.article_id ==
                                       article_id).filter(Article.user_id == user_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    return None

# Duplicate


@router.post("/{article_id}/duplicate", status_code=201)
def duplicate(article_id: str, article: ArticleUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user = get_user(db, api_key)
    article = db.query(Article).filter(Article.article_id ==
                                       article_id).filter(Article.user_id == user.id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    duplicate_article = Article(
        language=article.language,
        main_keywords=article.main_keywords,
        urls=article.urls,
        status=article.status,
        keywords=article.keywords,
        heading_data=article.heading_data,
        created_at=datetime.now(),
        user=user
    )

    db.add(duplicate_article)
    db.commit()
    db.refresh(duplicate_article)

    return duplicate_article


def update_article(article_id: str, article_update: ArticleUpdate, db: Session):
    article = db.query(Article).get(article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for attr, value in article_update.dict(exclude_unset=True).items():
        setattr(article, attr, value)

    db.commit()
    db.refresh(article)

    return article

# Headers Scrapping


def build_prompts(article, db):
    heading_data = article.heading_data
    prompt_base = get_prompt_base(heading_data["data"], db)
    data = heading_data["data"]
    scan_sections(data, prompt_base, data)
    # article.heading_data["data"] = data
    return data


# Get All Headers
def get_all_titles(data):
    titles = []
    for obj in data:
        titles.append(obj['text'])
        if 'children' in obj:
            titles.extend(get_all_titles(obj['children']))
    return titles

# Get Previous Object


def get_previous_sibling(data, target_id, is_parent=False):
    if is_parent == False:
        data = find_parent_object(target_id, data)

    for i in range(len(data)):
        if data[i]["id"] == target_id:
            if i > 0:
                return data[i - 1]
            else:
                return None
    return None

# Get Next Object


def get_next_sibling(data, target_id, is_parent=False):
    if is_parent == False:
        data = find_parent_object(target_id, data)

    for i in range(len(data)):
        if data[i]["id"] == target_id:
            if i < len(data) - 1:
                return data[i + 1]
            else:
                return None
    return None

# Find Parent Object


def find_parent_object(target_id, original_data):
    for item in original_data:
        if item.get("id") == target_id:
            return None  # No parent object found for the root level
        elif "children" in item:
            for child in item["children"]:
                if child.get("id") == target_id:
                    return item
                else:
                    parent = find_parent_object(
                        target_id, child.get("children", []))
                    if parent is not None:
                        return parent
    return None  # Target ID not found


def get_variables(item, original_data):
    current_header = item.get("text")
    keywords = item.get("keywords")
    more_info = item.get("more_info")

    # Parent Header
    parent_header_object = find_parent_object(item.get("id"), original_data)
    parent_header = "" if parent_header_object is None else parent_header_object["text"]

    parent_object = original_data if parent_header_object is None else parent_header_object.get(
        "children")
    # Previous Header
    previous_header_object = get_previous_sibling(parent_object, item.get("id"), True)
    previous_header = "" if previous_header_object is None else previous_header_object["text"]

    # Next Header
    next_header_object = get_next_sibling(parent_object, item.get("id"), True)
    next_header = "" if next_header_object is None else next_header_object["text"]

    # H1 Title : First One
    h1_title = original_data[0].get("text") if original_data is not None and original_data[0] is not None else "" 

    # All Headers
    all_headers_list = get_all_titles(original_data)
    all_header = ", ".join(all_headers_list)

    return current_header, parent_header, keywords, more_info, previous_header, next_header, h1_title, all_header
    
# Generate Prompt
def generate_value(item, prompt_base, original_data):
    if 'prompt_id' in item and item['prompt_id'] in prompt_base:
        current_header, parent_header, keywords, more_info, previous_header, next_header, h1_title, all_header = get_variables(item, original_data)
        
        # item['prompt_txt'] = prompt_base[item['prompt_id']].text_area
        
        # item['tag'] = parent_header
        # item['previous'] = previous_header
        # item['next'] = next_header
        # item['h1_title'] = h1_title
        # item['all_header'] = all_header


        # Variables pass to Prompt Text -> Prompt Parsed Text
        # Prompt Parsed Text to OpenAI - Generated Text
        # Save Generated Text to response key of heading_data
        
        prompt_text = prompt_base[item['prompt_id']].text_area
        prompt_parsed_text = prompt_text.format(
            current_header=current_header,
            parent_header=parent_header,
            keywords=keywords,
            more_info=more_info,
            previous_header=previous_header,
            next_header=next_header,
            h1_title=h1_title,
            all_header=all_header
        )
        
        item['prompt_parsed_text'] = prompt_parsed_text
        
    else:
        item['prompt_parsed_text'] = ''


def scan_sections(data, prompt_base, original_data):
    for item in data:
        generate_value(item, prompt_base, original_data)
        if 'children' in item:
            scan_sections(item['children'], prompt_base, original_data)

# Prepare Prompt Base which includes only needy prompts; It will reduce DB Calls


def get_prompt_base(data, db):
    prompt_ids = extract_prompt_ids(data)
    used_prompts = db.query(Prompt).filter(
        Prompt.prompt_id.in_(prompt_ids)).all()
    prompt_base = {prompt.prompt_id: prompt for prompt in used_prompts}
    return prompt_base

# Extract All Prompt Ids


def extract_prompt_ids(data):
    prompt_ids = []

    if isinstance(data, dict):
        if "prompt_id" in data:
            prompt_ids.append(data["prompt_id"])

        for value in data.values():
            if isinstance(value, (dict, list)):
                prompt_ids.extend(extract_prompt_ids(value))

    elif isinstance(data, list):
        for item in data:
            prompt_ids.extend(extract_prompt_ids(item))

    return prompt_ids
