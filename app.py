from datetime import datetime
from flask import Flask, Response
import time
import pandas as pd
import requests
import logging
import json
import random
import string
from app.FlowHandler import FlowHandler


with open('config.json', 'r') as f:
    config = json.load(f)

INSTANCE = config['INSTANCE']
SURVEYID = config['SURVEY']
FORMID = config['FORM']
SECRET = config['SECRET']
TOKEN = config['TOKEN']

requestURI = 'https://api.akvo.org/flow/orgs/' + INSTANCE + '/surveys/' + SURVEYID
formURI = 'https://api.akvo.org/flow/orgs/' + INSTANCE + '/form_instances?survey_id=' + SURVEYID + '&form_id=' + FORMID

logging.basicConfig(level=logging.WARN)
start_time = time.time()
app = Flask(__name__)


def checkTime(x):
    total_time = x - start_time
    spent = time.strftime("%H:%M:%S", time.gmtime(total_time))
    return spent

def refreshData():
    tokens = requests.post(TOKEN, SECRET).json();
    return tokens['refresh_token']

def getAccessToken():
    account = {
        'client_id':'curl',
        'refresh_token': refreshData(),
        'grant_type':'refresh_token'
    }
    try:
        account = requests.post(TOKEN, account).json();
    except:
        logging.error('FAILED: TOKEN ACCESS UNKNOWN')
        return False
    return account['access_token']

def getResponse(url):
    header = {
        'Authorization':'Bearer ' + getAccessToken(),
        'Accept': 'application/vnd.akvo.flow.v2+json',
        'User-Agent':'python-requests/2.14.2'
    }
    response = requests.get(url, headers=header).json()
    return response

def getAll(url):
    dataPoints = []
    data = getResponse(url)
    formInstances = data.get('formInstances')
    for dataPoint in formInstances:
        dataPoints.append(dataPoint)
    try:
        print(checkTime(time.time()) + ':: GET DATA FROM[' + url + ']')
        url = data.get('nextPageUrl')
        getAll(url)
    except:
        print(checkTime(time.time()) + ':: DOWNLOAD COMPLETE')
    return dataPoints

@app.route('/')
def download():
    csv_filename = "_".join([INSTANCE,SURVEYID, FORMID]) + ".csv"
    randomString = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    csv_output = datetime.strftime(datetime.now(), "%Y_%m_%d_%H%m_"  + randomString + csv_filename)
    apiData = getResponse(requestURI).get('forms')
    questions = lambda x : [{'id':a['id'],'name':a['name'],'questions':details(a['questions'])} for a in x]
    details = lambda x : [{'id':a['id'],'name':a['name'].replace(' ','_'),'type':a['type']} for a in x]
    meta = questions(apiData[0]['questionGroups'])
    mt = pd.DataFrame(meta)
    groupID = mt['id'][0]
    metadata = mt['questions'][0]
    dataPoints = getAll(formURI)
    output = pd.DataFrame(dataPoints)
    print(checkTime(time.time()) + ':: TRANSFORMING')
    for qst in metadata:
        qName = qst['name'].replace('_',' ')
        qId = str(qst['id'])
        qType = qst['type']
        output[qName] = output['responses'].apply(lambda x: FlowHandler(x[groupID],qId,qType))
        if qType == 'GEO':
            output[qName+'_lat'] = output[qName].apply(lambda x: x[0] if x is not None else x)
            output[qName+'_long'] = output[qName].apply(lambda x: x[1] if x is not None else x)
            output = output.drop([qName], axis=1)
    output = output.drop(['responses'], axis=1)
    print(checkTime(time.time()) + ':: SAVING NEW CSV FILE')
    output.to_csv(csv_output, index=False)
    with open(csv_output) as fp:
         csv = fp.read()
    return Response(csv,mimetype="text/csv",headers={"Content-disposition":"attachment; filename=" + csv_output})

if __name__=='__main__':
    app.config.update(DEBUG=True)
    app.run(host='0.0.0.0', debug=True, port=5000)
