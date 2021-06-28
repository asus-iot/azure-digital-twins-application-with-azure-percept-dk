import json
import logging
import os

import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.digitaltwins.core import DigitalTwinsClient


def main(event: func.EventGridEvent):
    try:
        event_type = event.event_type
        event_json = event.get_json()
        logging.info('event_type: %s', event_type)
        logging.info(event_json)
        device_id = event_json['twin']['deviceId']
        model_id = event_json['twin']['modelId']
        logging.info('device_id: %s', device_id)
        logging.info('model_id: %s', model_id)

        if model_id == '':  # prevent module created event
            dt_url = os.environ['DT_URL']
            dt_percept_model_id = os.environ['DT_PERCEPT_MODEL_ID']
            logging.info('dt_url: %s', dt_url)

            credential = ManagedIdentityCredential()
            service_client = DigitalTwinsClient(dt_url, credential)
            if event_type == 'Microsoft.Devices.DeviceCreated': # other events: https://docs.microsoft.com/en-us/azure/event-grid/event-schema-iot-hub?tabs=event-grid-event-schema
                temporary_twin = {
                    '$metadata': {
                        "$model": dt_percept_model_id
                    },
                    '$dtId': device_id
                }
                logging.info('=== try to create device twin ===')
                created_twin = service_client.upsert_digital_twin(device_id, temporary_twin)    # update or insert dt
                logging.info('device twin: ' + json.dumps(created_twin))
            else:
                logging.info('Event: {}'.format(event_type))
    except Exception as e:
        logging.error('Failed: '+ str(e))
    logging.info('done')