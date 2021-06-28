import json
import logging
import base64
import os

import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.digitaltwins.core import DigitalTwinsClient


def main(event: func.EventGridEvent):
    try:
        event_json = event.get_json()
        device_id = event_json['systemProperties']['iothub-connection-device-id']
        logging.info('device_id: %s', device_id)
        data_encode = event_json['body']
        logging.info('data_encode: %s', data_encode)
        data = base64.b64decode(data_encode)
        logging.info('data: %s', data)

        try:
            data_dict = json.loads(data)
            logging.info(data_dict)
            if 'NEURAL_NETWORK' in data_dict.keys():
                counts = {}
                for item in data_dict['NEURAL_NETWORK']:    # count label
                    label = item['label']
                    if label in counts.keys():
                        counts[label] += 1
                    else:
                        counts[label] = 1
                logging.info(counts)
                counts_string = json.dumps(counts)
                dt_url = os.environ['DT_URL']
                logging.info('dt_url: %s', dt_url)

                credential = ManagedIdentityCredential()
                service_client = DigitalTwinsClient(dt_url, credential)
                get_twin = service_client.get_digital_twin(device_id)
                logging.info('twin now: ' + json.dumps(get_twin))

                patch = [
                    {
                        "op": "replace" if 'ObjectDetect' in get_twin else 'add',
                        "path": "/ObjectDetect",
                        "value": counts_string
                    }
                ]
                updated_twin = service_client.update_digital_twin(
                    device_id, patch)
                logging.info('twin after: ' + json.dumps(updated_twin))
        except ValueError as e:
            logging.info('fail to parse string to json')
    except Exception as e:
        logging.error('Failed: ' + str(e))
    logging.info('done')
