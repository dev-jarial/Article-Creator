from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ToolStrategy:
    def check_status(self, resource, config):
        pass

    def process(self, resource, config):
        pass

    def apply(self, resource, config):
        pass

    def save_at_device(self, file_url= None, subpath = None):
        file_name = os.path.basename(file_url)
        response = requests.get(file_url)
        if subpath != None:
            subpath = str(subpath)+'/'+file_name
        else:
            subpath = file_name

        file_url = subpath
        print(subpath)
        print(file_url)
        open(file_url, "wb").write(response.content)

        return file_name

    def log(*arguments):
        log_file = os.environ.get("LOG_FILE")
        with open(log_file, "a") as file:
            # Writing data to a file
            file.write("\n\n\n Log: {0} \n".format(datetime.now()))
            for arg in arguments:
                file.write("\n")
                file.write(str(arg))