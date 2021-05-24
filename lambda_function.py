import json 
import os 
from nacl.signing import VerifyKey 
from nacl.exceptions import BadSignatureError 

def lambda_handler(event, context):

    PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']
    
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    
    signature = event['headers']["x-signature-ed25519"] 
    timestamp = event['headers']["x-signature-timestamp"] 
    body = event['body']

    try: 
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        body = json.loads(event['body'])
        if body["type"] == 1:
            return {
             'statusCode': 200, 
             'body': json.dumps({'type': 1})
         }
        else:
            return {
             'statusCode': 200, 
             'body': json.dumps({'type': '4', 'data': {'content': 'This worked'}})
         }
    except (BadSignatureError) as e:
        return {
             'statusCode': 401, 
             'body': json.dumps("Bad Signature")
         } 
    