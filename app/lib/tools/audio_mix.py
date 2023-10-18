import os
import requests
import json
from urllib.parse import urlencode
from .tool_strategy import ToolStrategy
from datetime import date
from app.db.session import SessionLocal
from app.models.predictions.prediction import Prediction
from sqlalchemy.orm.attributes import flag_modified

import zipfile
import urllib.request

class AudioMix(ToolStrategy):
    def __init__(self):
        self.url = "https://tonn.roexaudio.com/"
        self.headers = {'Content-Type': 'application/json'}


    def apply(self, resource, config):
        extraa = self.process(resource=resource, config=config)
        # extra_data = json.dumps(extraa)

        dbt = SessionLocal()
        prediction = dbt.query(Prediction).filter_by(id=config['id']).first()
        prediction.extra_data = extraa
        dbt.commit()
        dbt.close()

        return self.check_status(resource=resource, config=config)

    def post_multitrack(self, payload):
        
        url = self.url+'multitrackmix'
        querystring = {"key":"AIzaSyAzMhnWIYscIFkR2sAPvZlokyJc3cEky8w"}

        response = requests.post(url, json=payload, headers=self.headers, params=querystring)

        parsed_response = response.json()

        return parsed_response.get('multitrack_task_id')
    
    def get_multitrack(self, multitrackid):
        url = self.url+'multitrackstatus/'+multitrackid
        # Need to Reuse
        querystring = {"key":"AIzaSyAzMhnWIYscIFkR2sAPvZlokyJc3cEky8w"}

        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, params=querystring)
        parsed_response = response.json()
        return parsed_response

    def process(self, resource, config):

        # File Data Preparation
        track_data = []
        for file in resource["files"]:
            file.params["isStem"] = file.params["isStem"]
            track_data.append(file.params)

        data = {
                "multitrackData": {
                    "trackData": track_data,
                    "musicalStyle": config["musicalStyle"],
                    "returnUnmixedTrack": config["returnUnmixedTrack"],
                    "createMaster": config["createMaster"],
                    "desiredLoudness": config["desiredLoudness"],
                    "returnStems": config["returnStems"]
                }
        }
        print(data)
        payload = data

        request_id = self.post_multitrack(payload)

        return {
            'request_id': request_id
        }
    
    # Save and Get Local URL
    def save_and_get_local_url(self, url):
        static_path = os.environ.get('STATIC_PATH')
        n_file_name = self.save_at_device(url, static_path)
        return os.environ.get('STATIC_URL')+n_file_name


    def check_status(self, resource, config):

        if 'request_id' in config and config['request_id'] is not None:
            
            multitrackid = config['request_id']

            multitrack = self.get_multitrack(multitrackid=multitrackid)

            status = multitrack.get('multitrack_task_data').get('state')

            dbt = SessionLocal()
            prediction = dbt.query(Prediction).filter_by(id=config['id']).first()
            prediction.extra_data['status'] = status
            flag_modified(prediction, "extra_data")

            dbt.commit()
            dbt.close()

            if status == 'MIX_TASK_COMPLETED' or status == 'MASTERING_TASK_COMPLETED':
                # If Mastering Set Requested Then Hit a Call 

                url = multitrack.get('multitrack_task_data').get('download_url_mixed')

                # Save Locals
                file_url = self.save_and_get_local_url(url)


                # Grab Stems if Any
                stems = multitrack.get('multitrack_task_data').get('stems')
                # Save Local
                stems = [self.save_and_get_local_url(value) for key, value in stems.items()]

                zip_url = ''
                if stems:
                    print(stems)
                    zip_filename = multitrackid+"_file.zip"
                    static_path = os.environ.get('STATIC_PATH')
                    zip_file = zipfile.ZipFile(static_path+zip_filename, "w")
                    zip_url = os.environ.get('STATIC_URL')+zip_filename
                    for url in stems:
                        # Get the file name from the URL
                        # filename = url.split("/")[-1]
                        filename = os.path.basename(url)
                        # Download the file
                        filepath = static_path+filename
                        # urllib.request.urlretrieve(url, static_path+filename)
                        # Add the file to the zip file
                        zip_file.write(filepath, arcname=filename)
                        # Remove the downloaded file
                        # os.remove(filename)

                    zip_file.close()

                    
            
                return {
                    'success': True,
                    'files': json.dumps({
                        'download_url_mixed': multitrack.get('multitrack_task_data').get('download_url_mixed'),
                        'download_url_unmixed': multitrack.get('multitrack_task_data').get('download_url_unmixed'),
                        'file_url': file_url,
                        'stems': stems,
                        'zipUrl': zip_url
                    })
                }

        return {
            'success': False
        }