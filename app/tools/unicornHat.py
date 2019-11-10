import json
import os

import boto3
import botocore

from app import settings
import hashlib

with open(os.path.join(settings.APP_STATIC, 'KEYS/aws.json'))as f:
    aws_config = json.load(f)

client = boto3.client('lambda', region_name='eu-west-2',
                      aws_access_key_id=aws_config['aws_access_key_id'],
                      aws_secret_access_key=aws_config['aws_secret_access_key'])


def main(password, value=None):
    def response_to_json(response):
        response_payload = json.loads(response['Payload'].read().decode("utf-8"))
        return response_payload['state']['reported']

    def get_current_color():
        response = client.invoke(
            FunctionName='unicorn_GET',
            InvocationType='RequestResponse',
            LogType='Tail',
        )
        return response_to_json(response)


    def send_new_colour(colour):

        try:
            rgb = tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))

            payload = [{"block_colour": str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2])}]
            response = client.invoke(
                FunctionName='unicornHat_Publish',
                InvocationType='RequestResponse',
                LogType='Tail',
                Payload=json.dumps(payload)
            )
            return get_current_color()
        except Exception as e:
            print(e)
    if not password:
        return None

    if password.hexdigest() == aws_config['app_pass']:

        if not value:
            try:

                value = get_current_color()
            except botocore.exceptions.EndpointConnectionError:
                return {"error": "Unable to connect to IOT device"}
            return {"current_colour": value}
        else:
            value = send_new_colour(value)
            return {"current_colour": value}
    else:
        return {"error": "Incorrect Password"}
