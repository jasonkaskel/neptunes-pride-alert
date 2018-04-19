import json
from botocore.vendored import requests
import os
import boto3

def fetch_auth():
    # TODO store auth token in dynamoDB and only fetch a new one if a request 401s
    response = requests.post(
        'https://np.ironhelmet.com/arequest/login',
        data={'type':'login', 'alias':os.environ['USERNAME'], 'password':os.environ['PASSWORD']})
    # TODO raise (and reschedule? notify?) on non-200/response.cookies['auth'] not present
    return response.cookies['auth']

def fetch_report():
    response = requests.post(
        'https://np.ironhelmet.com/trequest/order',
        headers={'Accept-Language': 'en-US,en;q=0.9',
                 'Accept': 'application/json, text/javascript, */*; q=0.01'},
        cookies=dict(auth=fetch_auth()),
        data={'type':'order',
              'order':'full_universe_report',
              'game_number':os.environ['GAME_NUMBER']})
    # TODO exception handling
    return json.loads(response.text)['report']

def calculate_coming_at_me(player_id, report, previous_at_me):
    fleets = report['fleets']
    stars = report['stars']
    my_stars = {k:star for (k,star) in stars.items() if str(star['puid']) == str(player_id)}
    my_star_ids = [id for id in my_stars]
    at_me = [fleet for (k,fleet) in fleets.items() if str(fleet['puid']) != str(player_id) and
                                                      len(fleet['o']) > 0 and
                                                      str(fleet['o'][0][1]) in my_star_ids]
    if (len(at_me) > 0): send_warnings(at_me, my_stars, previous_at_me)
    return at_me

def send_warnings(at_me, my_stars, previous_at_me):
    at_me_fleet_ids = [fleet['uid'] for fleet in at_me]
    new_at_me_fleet_ids = [fleet for fleet in at_me_fleet_ids if fleet not in previous_at_me]
    new_at_me = [fleet for fleet in at_me if fleet['uid'] in new_at_me_fleet_ids]
    warnings = [
        "{} is coming at your star {}!".format(
            fleet['n'], my_stars[str(fleet['o'][0][1])]['n']) for fleet in new_at_me]
    if (len(warnings) > 0):
        response = requests.post(
          os.environ['TWILIO_URL'],
          data={'To': os.environ['TWILIO_TO'],
                'From': os.environ['TWILIO_FROM'],
                'Body': ', '.join(warnings)}, 
          auth=(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN']))

def create_at_me_table(client):
    response = client.list_tables()
    if ('AtMe' not in response['TableNames']):
        client.create_table(
            AttributeDefinitions=[{
                'AttributeName': 'Id',
                'AttributeType': 'S'}],
            TableName='AtMe',
            KeySchema=[{
                'AttributeName': 'Id',
                'KeyType': 'HASH'}],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5})

def fetch_previous_as_me(client, player_id):
    db_key = "{}:{}".format(os.environ['GAME_NUMBER'], player_id)
    response = client.get_item(TableName='AtMe', Key={'Id': {'S': db_key}})
    return [] if 'Item' not in response else [int(fleet_id) for fleet_id in response['Item']['FleetIds']['NS']]

def store_at_me(client, player_id, at_me):
    db_key="{}:{}".format(os.environ['GAME_NUMBER'], player_id)
    fleet_ids = ['-1'] if len(at_me) == 0 else [str(fleet['uid']) for fleet in at_me]
    client.put_item(TableName='AtMe', Item={'Id': {'S': db_key}, 'FleetIds': {'NS': fleet_ids}})

def lambda_handler(event, context):
    report = fetch_report()
    player_id = report['player_uid']
    dynamo_client = boto3.client('dynamodb')
    create_at_me_table(dynamo_client)
    previous_at_me = fetch_previous_as_me(dynamo_client, player_id)
    at_me = calculate_coming_at_me(player_id, report, previous_at_me)
    store_at_me(dynamo_client, player_id, at_me)

