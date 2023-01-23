# Author: Roy
import sys
from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.core.utils import EndpointConfig
from rasa.core.channels.rest import RestInput
import json
import os

# from custom_connector import ENG
# from rasa.core.tracker_store import RedisTrackerStore
# from db.tracker_store_connection import load_config
# from logger_conf.logger import get_logger
# from raven import Client

import spacy

# logger = logging.get_logger(__name__)  # name of the module

## redis connection for trackers
# redis_config = load_config()
# redis_db_no = redis_config['redis_tracker_store']['db_tracker']


# Loading Spacy Model for ENGLISH
spacy_model_obj = spacy.load("en_core_web_md")


def serve(port, i):
    

    try: 
        chan = RestInput()
        
        # logger.info("\nLoading NLU Model\n")
        # logger.info("Environment is : "+str(environment))
        
        # if environment == "prod":
        #     nlu_interpreter = RasaNLUInterpreter(parameters["nlu"],spacy_model_obj=spacy_model_obj)
        #     action_url = "http://"+ os.environ["ACTION_SERVER"] + "/webhook"
        #     logger.info("Action url is : "+str(action_url))
        #     act = EndpointConfig(url=action_url)
       
        # elif environment == "demo":
        #     nlu_interpreter = RasaNLUInterpreter( parameters["nlu"], spacy_model_obj=spacy_model_obj)
        #     # action_url = "http://" + os.environ["ACTION_SERVER"] + "/webhook"

        
        nlu_interpreter = RasaNLUInterpreter("models/nlu/",spacy_model_obj=spacy_model_obj)
        action_url = "http://" + "localhost:5055" + "/webhook"
        act = EndpointConfig(url=action_url)

        agent = Agent.load("models/20230118-132516.tar.gz", interpreter = nlu_interpreter, action_endpoint=act)

        # logger.info("\n Core Model Loaded and Ready to Serve!\n")
        # logger.info("="*100)
        # logger.info("Started on port -> " + str(port))
        
        agent.handle_channels([chan], int(port))
    
    except Exception as e:
        
        print("Enter the exception block",e)

if __name__ == '__main__':
    print("Enter the Main Block ")
    
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

    ps = psutil.Process()
    cpul = ps.cpu_affinity()  # CPU affinity list for the process
    # if environment == "prod":
    #     no_cpu = os.environ["no_process"]
    #     first_port = 9001
    # else:
    no_cpu = os.environ["no_process"]
    print(f"No of CPU :{no_cpu} ")
    # no_cpu = 1
    first_port = 5002
    
    ports = []
    for i in range(int(no_cpu)):
        portnum = first_port + i
        ports.append(str(portnum))
    port_pool = cycle(ports)
    
    print("Enter Main Block -- Ports ")

    if (len(cpul) == int(no_cpu)):
        print("Enter If Block of Main")
        # Exclusiveness in set. Bind to cpu list
        for i in cpul:
            p = multiprocessing.Process(target=serve, args=(int(next(port_pool)), i))
            p.start()
    else:
        # No exclusiveness. Bind to first "no_cpu" cpus.
        print("Enter else Block of Main -- No CPU Triggring")
        for i in range(0, int(no_cpu)):
            p = multiprocessing.Process(target=serve, args=(int(next(port_pool)), i))
