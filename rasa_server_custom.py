# Author: Roy

# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning) 
import sys
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.utils import EndpointConfig
from rasa.model import get_model, get_model_subdirectories
from rasa.core.run import configure_app 


# from custom_connector import ENG
# from channel import RestInput
# from REST import RestInput
# from rasa.core.channels.rest import RestInput
from custom_channel import MyioInput

import json
import os

# chan is the custom channel connector required to handle input and output of the rasa stack

import spacy

# logger = get_logger(__name__)  # name of the module

## redis connection for trackers
# redis_config = load_config()
# redis_db_no = redis_config['redis_tracker_store']['db_tracker']
    
# Loading Spacy Model for ENGLISH
spacy_model_obj = spacy.load("en_core_web_md")


# my_channel = MyioInput()
# rest_channel._extract_input_channel()
def serve(port):
    """load the model and nlu file and serve locally
    """
    try: 
        print("Enter Serve function -- Try Block ")
        chan = MyioInput()
        
        nlu_interpreter = RasaNLUInterpreter("models/nlu/",spacy_model_obj=spacy_model_obj)  #,spacy_model_obj=spacy_model_obj
        action_url = "http://"+ "localhost:5055" + "/webhook"

        act = EndpointConfig(url=action_url)

        agent = Agent.load("models/20230118-132516.tar.gz", interpreter = nlu_interpreter, action_endpoint=act)

        print("Enter Serve function -- agent is loaaded ")

        agent.handle_channels([chan], int(port)) # method is not available in rasa 2.8
        
        print("Enter Serve function ---Try Block exection Done")
    
    except Exception as e:

        print("Enter the exception block",e)
        
        
        
#-------------------------------------------------------------- 
        
# model_path = get_model("/home/janmejay/Rasa bot/bot3/models")

# def run(serve_forever=True):
    
#     _, nlu_model = get_model_subdirectories(model_path)
#     interpreter = RasaNLUInterpreter(nlu_model)
#     action_url = "http://"+ "localhost:5055" + "/webhook"
#     action_endpoint = EndpointConfig(url=action_url)
#     agent = Agent.load(model_path, interpreter=interpreter, action_endpoint=action_endpoint)
#     input_channel = my_channel()
#     if serve_forever:
#         configure_app(input_channel)
#     return agent


#-----------------------------------------------------------------

if __name__ == '__main__':
    # run()
    
    import datetime
    import multiprocessing
    import os
    import socket
    import subprocess
    import threading
    import time
    from concurrent import futures
    from itertools import cycle
    import psutil
    import requests
    from pytz import timezone
    
    print("Enter the Main Block ")
    ps = psutil.Process()
    cpul = ps.cpu_affinity()
    print(f"cpul : {cpul}")# CPU affinity list for the process
    # if environment == "prod":
    #     no_cpu = os.environ["no_process"]
    #     first_port = 9001
    # else:
    no_cpu = 1
    first_port = 5002
        
    print("Enter Main Block -- CPU Affinity")
    
    ports = []
    for i in range(int(no_cpu)):
        portnum = first_port + i
        ports.append(str(portnum))
    port_pool = cycle(ports)
    
    print("Enter Main Block -- Ports ")

    if (no_cpu == 1):
        print("Enter If Block of Main")
        # Exclusiveness in set. Bind to cpu list
        # for i in cpul:
        p = multiprocessing.Process(target=serve, args=[5002])
        p.start()
    else:
        print("Enter else Block of Main")
        # No exclusiveness. Bind to first "no_cpu" cpus.
        # for i in range(0, int(no_cpu)):
        p = multiprocessing.Process(target=serve, args=(int(next(port_pool))))



# serve(1024)