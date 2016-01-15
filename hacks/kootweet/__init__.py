import flask
import xml.etree.cElementTree as ET
import requests
from urllib.parse import unquote
from requests_oauthlib import OAuth1
# cofidential credentials
from hacks.kootweet.config import *

app = flask.Blueprint('app', __name__, template_folder='templates')

app_url = 'https://hacks-rakheg.rhcloud.com/kootweet/'
dbUrl = 'https://kookoosocialhack.firebaseio.com/'

@app.route('/<master>')
def home(master):
	if not constant_time_compare(master, master_key):
		return 'Tough luck buddy! ^_^'
	
	global params, cid
	params = flask.request.args
	cid = params.get('cid')[-10:]
	
	event = params.get('event')
	if event == 'NewCall':
		return newCall()
	elif event == 'Record':
		return record()
	elif event == 'NewSms':
		return newSms()
	
	response = ET.Element('response')
	ET.SubElement(response, 'playtext').text = 'LOL'
	ET.SubElement(response, 'hangup')
	return kookooResponse(response)

@app.route('/account/<number>/<uid>')
def account(number, uid):
	loggedIn = int(cidExists(number))
	customToken = token(number, uid)
	return flask.render_template('kootweet-number-login.html',
								 token=customToken, number=number, loggedIn=loggedIn)

@app.route('/callMe/<number>')
def callMe(number):
	callUrl = 'http://www.kookoo.in/outbound/outbound.php'
	response = requests.get(callUrl, params= {'phone_no': number,
											  'caller_id': '918067947419',
											  'api_key': kookoo_api_key,
											  'url': app_url + master_key}).text
	return response, 200, {'Content-Type': 'application/xml; charset=utf-8'}

def newCall():
	if cidExists(cid):
		response = ET.Element('response', {'filler': 'yes'})
		ET.SubElement(response, 'playtext').text = 'Welcome to Koo Tweet. Press hash to stop recording.'
		import time, random
		ET.SubElement(response, 'record', {'maxduration': '120'}).text = str(time.time()) + str(random.random())
		ET.SubElement(response, 'playtext').text = 'Koo Tweet posting'
	else:
		response = ET.Element('response')
		ET.SubElement(response, 'playtext').text = 'Welcome to Koo Tweet, a Koo koo Social Media Challenge app demo. Please log in to Twitter by clicking on your personal secret link sent to you via SMS. Created by Ruck Shuck R Heg day.'
		ET.SubElement(response, 'hangup')
		sendSms(cid, createSecretMsg(cid))
	return kookooResponse(response)

def record():
	recordingUrl = shortUrl(unquote(params.get('data')))
	status = 'Listen to my KooTweet ' + recordingUrl + '\n@OzonetelSystems @venturesity #KooTweetApp'
	postTweet(status)
	response = ET.Element('response')
	ET.SubElement(response, 'playtext').text = 'Have a nice day'
	ET.SubElement(response, 'hangup')
	return kookooResponse(response)

def newSms():
	message = unquote(params.get('message'))
	if 'gettweets' in message:
		try:
			koomsg(message)
		except Exception as e:
			print(e)
			sendSms(cid, 'Invalid KooTweet request!\nExample:\nkootweet gettweets 3\nkootweet gettweets 3 @username\nkootweet gettweets 3 #hashtag\nkootweet gettweets 3 your_query')
			return flask.jsonify(success=False, message='gettweets failed!')
	else:
		appendage = '\n@OzonetelSystems @venturesity #KooTweetApp'
		message = message[:140-len(appendage)] + appendage
		postTweet(message)
	return flask.jsonify(success=True)

def koomsg(args):
	auth = getTwitterOAuth()
	twitterUrl = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
	params = {}
	args = args.split()
	count = args[1] # args[0] is gettweets
	if count.isnumeric():
		if int(count) <= 100:
			params['count'] = count
			query = ' '.join(args[2:])
		else:
			sendSms(cid, 'Invalid! count must be less than or equal to 100')
			return
	else:
		count = 4
		query = ' '.join(args[1:])
	if query:
		if query[0] == '@':
			twitterUrl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
			params['screen_name'] = query
			tweetsArray = requests.get(twitterUrl, auth=auth, params= params).json()
		else:
			twitterUrl = 'https://api.twitter.com/1.1/search/tweets.json'
			params['q'] = query
			tweetsArray = requests.get(twitterUrl, auth=auth, params= params).json()['statuses']
	else:
		tweetsArray = requests.get(twitterUrl, auth=auth, params= params).json()
	tweetSms = ''
	for tweet in tweetsArray:
		tweetSms += formatTweet(tweet) + '\n\n'
	try:
		import os
		os.system('echo '+str(tweetsArray)+' | clip')
	except Exception as e: print(e)
	sendSms(cid, tweetSms)

def formatTweet(tw):
	tweetText = tw['text']
	for url in tw['entities']['urls']:
		tweetText = tweetText.replace(url['url'], url['display_url'])
	return '@{}\n{}\nRT{} FAV{}'.\
			format(tw['user']['screen_name'],
				   tweetText,
				   tw['retweet_count'],
				   tw['favorite_count'])

def postTweet(status):
	auth = getTwitterOAuth()
	twitterUrl = 'https://api.twitter.com/1.1/statuses/update.json'
	return requests.post(twitterUrl, auth=auth,
					   params= {'status': status}).text

def getTwitterOAuth():
	tokens = requests.get(dbUrl + 'credentials/{}.json'.format(cid),
						   params= {'auth': db_admin_secret}).json()
	return OAuth1(twitter_api_key, twitter_api_secret,
                  tokens['accessToken'], tokens['accessTokenSecret'])

def cidExists(cid):
	response = requests.get(dbUrl + 'credentials/{}.json'.format(cid),
						   params= {'auth': db_admin_secret}).text
	return response != 'null'

def createSecretMsg(cid):
	# get a unique ID from DB
	uid = requests.post(dbUrl + 'uid.json', data='"{}"'.format(cid)).json()['name']
	url = shortUrl('{}account/{}/{}'.format(app_url, cid, uid))
	return 'Your personal secret KooTweet url: ' + url

def sendSms(cid, msg):
	msgUrl = 'https://www.kookoo.in/outbound/outbound_sms.php'
	payload = {'phone_no': cid, 'api_key': kookoo_api_key, 'message': msg}
	print(requests.get(msgUrl, params= payload).text)

def token(number, uid):
	from firebase_token_generator import create_token

	auth_payload = {"uid": uid, "auth_data": number}
	options = {"debug": False}
	return create_token(db_admin_secret, auth_payload, options)

def shortUrl(longUrl):
	return requests.post('https://www.googleapis.com/urlshortener/v1/url',
						 params= {'key': urlshortener_apikey},
						 data= '{{ "longUrl": "{}" }}'.format(longUrl),
						 headers= {'Content-Type': 'application/json'}).json()['id']

def kookooResponse(ETdata):
	return xmlResponse(xmlToString(ETdata))

def xmlResponse(xmlString):
	return xmlString, 200, {'Content-Type': 'application/xml; charset=utf-8'}

def xmlToString(ETdata):
	return ET.tostring(ETdata, encoding='utf8', method='xml')

def remDbg(debugMsg):
	from datetime import datetime
	dateTimeNow = datetime.now().strftime('%y-%m-%d %H:%M:%S')
	requests.put(dbUrl + 'log/{}.json'.format(dateTimeNow), data='"{}"'.format(debugMsg))

def constant_time_compare(val1, val2):
	"""
	Returns True if the two strings are equal, False otherwise.

	The time taken is independent of the number of characters that match.

	For the sake of simplicity, this function executes in constant time only
	when the two strings have the same length. It short-circuits when they
	have different lengths.
	"""
	if len(val1) != len(val2):
		return False
	result = 0
	for x, y in zip(val1, val2):
		result |= ord(x) ^ ord(y)
	return result == 0
