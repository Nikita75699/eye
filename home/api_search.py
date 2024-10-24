import os
import time
import logging
import requests


def api_dicom():

    logging.info("start")
    time.sleep(30)
    response = requests.get('http://127.0.0.1:8000/appointment_search')
    response.raise_for_status()


while True:
    current_time = time.strftime("%H:%M:%S")
    if current_time == "20:00:00":
       api_dicom()

