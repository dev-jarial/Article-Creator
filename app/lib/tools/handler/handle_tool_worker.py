import json

from app.lib.tools.worker.tool_worker import ToolWorker
from app.lib.tools.audio_mix import AudioMix
from app.db.session import SessionLocal
from app.models.predictions.prediction import File


def get_tool_worker(prediction):

    tw = ToolWorker()

    # Local Path
    if 'local_url' in prediction:
        tw.add_resource('path', prediction['local_url'])

    # File Url
    if 'file_url' in prediction:
        tw.add_resource('url', prediction['file_url'])

    # File Objects
    dbt = SessionLocal()
   
    # Id of Prediction
    if 'id' in prediction:
        tw.add_config('id', prediction['id'])
        # Files Object
        files = dbt.query(File).filter(File.prediction_id == prediction['id']).all()
        dbt.close()
        tw.add_resource('files', files)
        
    #Input Parameters
    if 'inputs' in prediction and prediction['inputs'] is not None:
        inputs = json.loads(prediction['inputs'])

        if inputs is not None:
            # Stem Parameter
            if 'stems' in inputs:
                stems = str(inputs["stems"])+"stems"
                tw.add_config('model', stems)

            # Voice Parameter
            if 'voice' in inputs:
                voice = inputs['voice']
                tw.add_config('voice', voice)
        
            # Style Parameter
            if 'style' in inputs:
                style = inputs['style']
                tw.add_config('style', style)

            # Text Parameter
            if 'text' in inputs:
                text = inputs['text']
                tw.add_config('text', text)

            # Model Parameter
            if 'model' in inputs:
                model = inputs['model']
                tw.add_config('model', model)
            

            # Lyric Parameter
            if 'starting_lines' in inputs:
                starting_lines = inputs['starting_lines']
                tw.add_config('starting_lines', starting_lines)

            # Prompt for Mixing Assistant parameter
            if 'messages' in inputs:
                messages = inputs['messages']
                tw.add_config('messages', messages)

            # Return Unmixed Track
            if "returnUnmixedTrack" in inputs:
                returnUnmixedTrack = inputs['returnUnmixedTrack']
                tw.add_config('returnUnmixedTrack', returnUnmixedTrack)

            # Music Style
            if "musicalStyle" in inputs:
                musicalStyle = inputs["musicalStyle"]
                tw.add_config("musicalStyle", musicalStyle)

            # Create Master
            if "createMaster" in inputs:
                createMaster = inputs["createMaster"]
                tw.add_config("createMaster", createMaster)
            # Set DesiredLoudness if CreateMaster True=
            if "desiredLoudness" in inputs:
                desiredLoudness = inputs["desiredLoudness"]
                tw.add_config("desiredLoudness", desiredLoudness)
            else:
                # Default
                tw.add_config("desiredLoudness", "MEDIUM")

            # Set returnStems
            if "returnStems" in inputs:
                returnStems = inputs["returnStems"]
                tw.add_config("returnStems", returnStems)
            else:
                # Default
                tw.add_config("returnStems", False)
            
            print(tw)


            
    # Extra Parameters
    if 'extra_data' in prediction and prediction['extra_data'] is not None:
        extraa = json.loads(prediction['extra_data'])

        # request id
        if isinstance(extraa, dict) and 'request_id' in extraa:
            tw.add_config('request_id', extraa['request_id'])


    tool = prediction['name']
    strategy = None
    if tool == "AUDIO_MIX":
        strategy = AudioMix()

    if strategy:
        tw.set_tool(strategy)

    return tw