
<h1>Table of Contents<span class="tocSkip"></span></h1>
<div class="toc"><ul class="toc-item"></ul></div>


```python
from datetime import datetime
import time
import pandas as pd
import requests
import logging
import json
from app.FlowHandler import FlowHandler
```


```python
with open('config.json', 'r') as f:
    config = json.load(f)
```


```python
INSTANCE = config['INSTANCE']
SURVEYID = config['SURVEY']
FORMID = config['FORM']
SECRET = config['SECRET']
TOKEN = config['TOKEN']
dataPoints = []
```


```python
requestURI = 'https://api.akvo.org/flow/orgs/' + INSTANCE + '/surveys/' + SURVEYID
formURI = 'https://api.akvo.org/flow/orgs/' + INSTANCE + '/form_instances?survey_id=' + SURVEYID + '&form_id=' + FORMID
```


```python
def checkTime(x):
    total_time = x - start_time
    spent = time.strftime("%H:%M:%S", time.gmtime(total_time))
    return spent
```


```python
def refreshData():
    tokens = requests.post(TOKEN, SECRET).json();
    return tokens['refresh_token']
```


```python
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
```


```python
def getResponse(url):
    header = {
        'Authorization':'Bearer ' + getAccessToken(),
        'Accept': 'application/vnd.akvo.flow.v2+json',
        'User-Agent':'python-requests/2.14.2'
    }
    response = requests.get(url, headers=header).json()
    return response
```


```python
def getAll(url):
    data = getResponse(url)
    formInstances = data.get('formInstances')
    for dataPoint in formInstances:
        dataPoints.append(dataPoint)
    try:
        url = data.get('nextPageUrl')
        getAll(url)
    except:
        return "done"
```


```python
def download():
    apiData = getResponse(requestURI).get('forms')
    questions = lambda x : [{'id':a['id'],'name':a['name'],'questions':details(a['questions'])} for a in x]
    details = lambda x : [{'id':a['id'],'name':a['name'].replace(' ','_'),'type':a['type']} for a in x]
    meta = questions(apiData[0]['questionGroups'])
    mt = pd.DataFrame(meta)
    groupID = mt['id'][0]
    metadata = mt['questions'][0]
    getAll(formURI)
    output = pd.DataFrame(dataPoints)
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
    csv_filename = "_".join([INSTANCE,SURVEYID, FORMID]) + ".csv"
    csv_output = datetime.strftime(datetime.now(), "%Y_%m_%d_%H%m_" + csv_filename)
    output.to_csv(csv_output, index=False)
    return "downloaded to " + csv_output
```


```python
download()
```




    'downloaded to 2019_10_31_2310_seap_312920912_288920912.csv'


