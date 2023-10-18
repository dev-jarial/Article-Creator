import database as db
import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from tools.handler.handle_tool_worker import get_tool_worker
import json

load_dotenv()

host: str = os.environ.get("DB_HOST")
username: str = os.environ.get("DB_USER")
password: str = os.environ.get("DB_PASSWORD")
db_name: str = os.environ.get("DB_NAME")

connection = db.create_server_connection(host, username, password)
db.use_db(connection, db_name=db_name)


def copyFile(file_url, file_id):
    try:
        r = requests.get(file_url, allow_redirects=True)
        url = urlparse(file_url)
        local_file =  os.path.join(os.environ.get('LOCAL_PATH'), os.path.basename(url.path))
        with open(local_file, 'wb')as file:
            file.write(r.content)

        sql = " UPDATE predictions_file SET local_url = '{0}' WHERE id = '{1}' ".format(local_file, file_id)
        db.execute(connection=connection, query=sql)

        return local_file

    except Exception as e:
            print("Execution failed:", e)
    
    return None


def processPrediction(prediction):
    sql = " UPDATE predictions_predictions SET status = 'processing' WHERE id = '{0}' ".format(prediction['id'])
    db.execute(connection=connection, query=sql)
    
    tw = get_tool_worker(prediction=prediction)
    # Process by Tool: It is kind of Preprocess
    extraa = tw.process()

    extra_data = json.dumps(extraa)

    sql = " UPDATE predictions_predictions SET extra_data = '{0}'  WHERE id = '{1}' ".format(extra_data, prediction['id'])

    db.execute(connection=connection, query=sql)
    


# Get predictions which are in starting

sql = " SELECT p.*, t.name, f.file_url, f.id as file_id, f.local_url FROM predictions_predictions p INNER JOIN predictions_tools t ON t.name = p.tool LEFT JOIN predictions_file f ON f.prediction_id = p.id WHERE p.status = 'starting' "

predictions = db.select_query(connection=connection, query=sql)

if predictions:
    for prediction in predictions:
        # TODO: Rethink about this
        if prediction["local_url"] == None:
            prediction["local_url"] = copyFile(prediction["file_url"], prediction['file_id'])
        processPrediction(prediction)


# Check The prediction is Completed or Not
# Currently it is Concrete for Audio Splitter. TODO: Need to Work on this to meet its dynamic level
def checkCompletion(prediction):

    tw = get_tool_worker(prediction=prediction)
   
    status_dict = tw.check_status()

    if status_dict['success'] == True:

        json_files = status_dict['files']

        print(json_files)

        sql = " UPDATE predictions_predictions SET status = 'succeeded', outputs = '{0}'  WHERE id = '{1}' ".format(json_files, prediction['id'])

        db.execute(connection=connection, query=sql)




sql = " SELECT p.*, t.name, f.file_url, f.id as file_id, f.local_url FROM predictions_predictions p INNER JOIN predictions_tools t ON t.name = p.tool LEFT JOIN predictions_file f ON f.prediction_id = p.id WHERE p.status = 'processing' "

processing_predictions = db.select_query(connection=connection, query=sql)

if processing_predictions:
    for prediction in processing_predictions:
        checkCompletion(prediction)


db.close(connection=connection)
