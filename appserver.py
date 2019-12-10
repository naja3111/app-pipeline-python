import boto3
import os
from botocore.exceptions import ClientError
from flask import Flask
from flask import render_template

app = Flask(__name__)

APP_SERVER_PORT = os.environ['APP_SERVER_PORT'] \
    if 'APP_SERVER_PORT' in os.environ else '8090'

# create dynamodb client
# use environment vars for creds otherwise use default creds
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

WEBSITE_TABLE = os.environ['WEBSITE_TABLE'] \
    if 'WEBSITE_TABLE' in os.environ else 'dynacorp'
TABLE = dynamodb.Table(WEBSITE_TABLE)


@app.route('/')
def root_page():
    template = 'index.html'
    requests = None
    try:
        app.logger.info('Attempting to connect to DynamoDB')
        response = TABLE.update_item(
            Key={
                'Metadata': 'website'
                },
            UpdateExpression='SET Requests = Requests + :incr',
            ExpressionAttributeValues={
                ":incr": 1
                },
            ReturnValues='UPDATED_NEW'
            )
        requests = response['Attributes']['Requests']
        app.logger.info('Updated website requests:', requests)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            # likely first website access
            try:
                TABLE.put_item(
                    Item={
                        'Metadata': 'website',
                        'Requests': 1
                    }
                )
            except Exception as e:
                return render_template('error.html', error=e)
            return render_template(template, requests=1)
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            return render_template('error.html',
                                   error='Database resource not found.')
        else:
            return render_template('error.html', error=e)
    except Exception as e:
        return render_template('error.html', error=e)

    return render_template(template, requests=requests)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=APP_SERVER_PORT)