# Akvo Flow CSV

Webhook to download CSV File with Flow API

### Clone the Repository

```
$ git clone https://github.com/dedenbangkit/akvo-flow-csv.git
$ cd akvo-flow-csv
```

### Install Requirements

```
$ pip install -r requirements.txt
```

### Edit Config file

```
$ cp config.json.example config.json
$ vim config.json
```

- SECRET.username : Your Email Address
- SECRET.password : Your Password
- INSTANCE : Instance ID (e.g. ***xxx***.akvoflow.org)
- SURVEY : Survey ID
- FORM : Form ID

### Run Server

```
$ python app.py

 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 953-947-058

```

Once server is running open your browser then download the CSV file from:

```http://localhost:5000```
