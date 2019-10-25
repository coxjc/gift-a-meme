import os
import uuid
import requests
import boto3
from flask import Flask, render_template, jsonify, request, redirect
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
#end flask setup
#start aws config
aws_key = os.environ['gam_aws_key']
aws_secret = os.environ['gam_aws_secret']
aws_bucket= os.environ['gam_aws_bucket']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
s3_url = 'https://s3.amazonaws.com/'
# next_url stores the meme to which the next user will be forwarded
next_url = 'https://i.ytimg.com/vi/JlhGrcaRTdo/maxresdefault.jpg'

aws = boto3.client(
    's3',
    aws_access_key_id=aws_key,
    aws_secret_access_key=aws_secret
)

#returns true if allowed extension
def allowed_file(filename):
        return '.' in filename and \
                           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    count = aws.get_object(Bucket=aws_bucket, Key='count')['Body'].read().decode('utf-8')
    return render_template('home.html', count=count)

@app.route('/new', methods=['POST'])
def new():
    #set uuid for image key
    key = str(uuid.uuid4())
    post = aws.generate_presigned_post(
            Bucket=aws_bucket, 
            Key=key,
            Fields={"acl": "public-read"},
            Conditions=[{"acl": "public-read"}]
    )
    files = {"file": request.files['file']}
    if request.files['file'].filename == '' or not allowed_file(request.files['file'].filename):
        return render_template('home.html', count=count, error='Invalid file type. Only images, please.')
    response = requests.post(post["url"], data=post["fields"], files=files)
    #update count

    count = int(aws.get_object(Bucket=aws_bucket, Key='count')['Body'].read().decode('utf-8'))
    aws.put_object(Bucket=aws_bucket, Key='count', Body=str(count + 1))
    to_show = aws.get_object(Bucket=aws_bucket, Key='next')['Body'].read().decode('utf-8')
    aws.put_object(Bucket=aws_bucket, Key='next', Body=key)
    to_show_url = s3_url + aws_bucket + '/' + to_show
    return render_template('result.html', old_url=to_show_url, count=count + 1) 

if __name__ == '__main__':
    app.run()
