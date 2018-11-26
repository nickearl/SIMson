# Generate a random event with dummy values
import sqlite3
from sqlite3 import Error
import time
import random
import analytics
import logging
from analytics.request import _session
import yaml
import os

#Config
with open("config.yml", 'r') as configfile:
	config = yaml.load(configfile)

#Uncomment below line to enable (SSL) proxying through Charles
#analytics.request._session.verify = str(config['segment']['charlesCertPath'])
logging.getLogger('segment').setLevel('DEBUG')

#Make sure WRITE_KEY was set as an environment var, otherwise default to a dummy value
if "WRITE_KEY" in os.environ:
	analytics.write_key = os.environ['WRITE_KEY']
	print("** Write key set, sending data to: ", analytics.write_key)
else:
	analytics.write_key = config['segment']['writeKey']
	print("** Write key not set, using dummy value (DATA WILL NOT BE SENT): ", analytics.write_key)

#Check for supplied DB file, else fall back to example file
if os.path.isfile('/data/data.db'):
	config['db']['path'] = '/data/data.db'

#Segment error logging
def on_error(error, items):
	print("** SEGMENT: An error occurred: ", error)

analytics.debug = True
analytics.on_error = on_error


#DB methods
def create_connection(db_file):

	print("** Attempting DB connection")
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
			print(e)
	return None

def getEventNames(conn):

	print("** Getting all event names")
	cur = conn.cursor()
	cur.execute("SELECT * FROM event_names")
	rows = cur.fetchall()
	return rows

def getRandEventName(conn):

	print("** Getting a random event name")
	cur = conn.cursor()
	cur.execute("SELECT * FROM event_names ORDER BY RANDOM() LIMIT 1")
	row = cur.fetchone()
	return str(row[1])

def getRandTraits(conn):

	print("** Generating set of random traits")
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	cur.execute("SELECT * FROM traits ORDER BY RANDOM() LIMIT 1")
	rows = cur.fetchone()
	keys = rows.keys()
	traits = {}
	for i, val in enumerate(rows[1:], 1):
		traits[keys[i]] = rows[i]
	return traits

def getRandEventProperties(conn, eventName):

	print("** Generating random set of event properties")
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	try:
		cur.execute("SELECT * FROM '"+eventName+"' ORDER BY RANDOM() LIMIT 1")
		rows = cur.fetchone()
		if type(rows) == type(None):
			return None
		else:
			keys = rows.keys()
			properties = {}
			for i, val in enumerate(rows[1:], 1):
				properties[keys[i]] = rows[i]
			return properties
	except (sqlite3.Error) as e:
		print(e)
		return None

def getRandPage(conn):

	print("** Getting a random page")
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()
	try:
		cur.execute("SELECT * FROM 'pages' ORDER BY RANDOM() LIMIT 1")
		rows = cur.fetchone()
		keys = rows.keys()
		page = Payload()
		page.name = rows[1]
		page.properties = {}
		for i, val in enumerate(rows[2:], 2):
			page.properties[keys[i]] = rows[i]
		return page
	except (sqlite3.Error) as e:
		print(e)
		return None

# Segment API wrapper methods
def segmentIdentify(conn, payload):

	validate = validatePayload(payload)
	if validate == True:
		analytics.identify(payload.userId, payload.traits, anonymous_id=payload.anonymousId)
	else:
		print("Discarding Identify request")

def segmentTrack(conn, payload):

	payload.name = getRandEventName(conn)
	page = getRandPage(conn)
	a = dict(page.properties)
	b = getRandEventProperties(conn, payload.name)
	x = a.copy()
	x.update(b)
	payload.properties = x
	validate = validatePayload(payload)
	if validate == True:
		analytics.track(payload.userId, event=payload.name, context=payload.context, properties=payload.properties, anonymous_id=payload.anonymousId)
	else:
		print("Discarding Track request")

def segmentPage(conn, payload):
	page = getRandPage(conn)
	payload.name = page.name
	payload.properties = page.properties
	validate = validatePayload(payload)
	if validate == True:
		analytics.page(payload.userId, name=payload.name, context=payload.context, properties=payload.properties, anonymous_id=payload.anonymousId)
	else:
		print("Discarding Page request")

def segmentScreen(conn, payload):
	page = getRandPage(conn)
	payload.name = page.name
	payload.properties = page.properties
	validate = validatePayload(payload)
	if validate == True:
		analytics.screen(payload.userId, name=payload.name, context=payload.context, properties=payload.properties, anonymous_id=payload.anonymousId)
	else:
		print("Discarding Screen request")

def pageSession(conn, payload):
	numRequests = random.randint(config['session']['requestsMin'],config['session']['requestsMax'])
	print("** Simulating web session")
	print("** Sending "+str(numRequests)+" random requests")
	for counter in range(numRequests):
		reqType = random.randint(0,1)
		delayTime = random.randint(config['session']['delayMin'],config['session']['delayMax'])
		if reqType == 0:
			print("Sending request "+str(counter)+" | Type: Page")
			segmentPage(conn, payload)
		else:
			print ("Sending request "+str(counter)+" | Type: Event")
			segmentTrack(conn, payload)
		print("** Waiting for "+str(delayTime)+" seconds before next request")
		time.sleep(delayTime)

def screenSession(conn, payload):
	numRequests = random.randint(config['session']['requestsMin'],config['session']['requestsMax'])
	print("** Simulating mobile/ott session")
	print("** Sending "+str(numRequests)+" random requests")
	for counter in range(numRequests):
		reqType = random.randint(0,1)
		delayTime = random.randint(config['session']['delayMin'],config['session']['delayMax'])
		if reqType == 0:
			print("** Sending request "+str(counter)+" | Type: Screen")
			segmentScreen(conn, payload)
		else:
			print ("** Sending request "+str(counter)+" | Type: Event")
			segmentTrack(conn, payload)
		print("** Waiting for "+str(delayTime)+" seconds before next request")
		time.sleep(delayTime)

def validatePayload(payload):
	if isinstance(payload, Payload) == False:
		print("** Error: payload is not an instance of Payload")
		return False
	elif isinstance(payload.name, type(None)):
		print("** Error: payload.name is None")
		return False
	elif isinstance(payload.properties, type(None)):
		print("**Error: payload.properties is None")
		return False
	else:
		return True

def sendDummySession(conn):
	# Generate session-level payload
	print("** Initializing dummy session")
	payload = Payload()
	payload.userId = random.randint(100000000,999999999)
	payload.anonymousId = payload.userId
	payload.traits = getRandTraits(conn)
	payload.context['traits'] = payload.traits
	segmentIdentify(conn, payload)
	# Pick between page and screen calls for the session
	deviceType = random.randint(0,1)
	if deviceType == 0:
		pageSession(conn, payload)
	else:
		screenSession(conn, payload)

class Payload:
	userId = 'user_12345'
	anonymousId = 'anon_12345'
	name = 'testEvent'
	traits = {
		'test1': 'val1',
		'test2': 'val2'
		}
	properties = {
		'prop1': 'prop_val1',
		'prop2': 'prop_val2'
		}
	context = {
		'traits': traits
		}

def main():
	db = config['db']['path']
	conn = create_connection(db)
	with conn:
		while True:
			sendDummySession(conn)
	conn.cursor().close()
	conn.close()

if __name__ == '__main__':
	main()