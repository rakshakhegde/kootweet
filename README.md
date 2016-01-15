# KooTweet

A highly scalable, NoSQL based, KooKoo app to securely call or text to directly tweet without any password. Also one can read tweets via incoming text based on username, hashtag or any other search query.

> Disclaimer: You are solely responsible for maintaining confidentiality of the URL sent via SMS and of the secret keys embedded in them. I, Rakshak R.Hegde, am not liable for any loss, direct or indirect, occured to you by using this application.

Call **08067947419** to start KooTweet'ing. Due to Kookoo restrictions, DND (Do Not Disturb) should be disabled and the complete app will work only between 9am - 9pm.

## Requirements to setup
- Python 2 or 3
- Libraries specified in setup.py needs to be manually or pip installed
- Kookoo account for calls and SMS
- Twitter Dev Account for API access
- Firebase Account for NoSQL Data Storage and secure Twitter and Custom Authentication
- Google Cloud Services Account for Google's URL Shortener API access

## KooTweet Application Flow
For the code flow, one can start tracing from flaskapp.py and delve into hacks/kootweet/\__init__.py for the actual Kookoo app. The static files (css, js and images) for the html file is stored in the dir at root called 'static/'.

When a new user calls:
- User is greeted and a personal secret SMS is sent which contains their secret key. This key prevents everyone from posting as someone else. This SMS is not be shared with anyone and the URL needs to be kept safely.
- User navigates to the URL sent and logs in using their twitter account. Without any entry of password, user is safely logged in for further calls and texts to KooTweet.

When a logged in user calls:
- User records his/her voice after the beep, for a maximum of 120 seconds (120 sec is set to prevent long audio files from getting deleted from Kookoo servers and also to not annoy Twitter users :wink:). Presses hash (#) to stop recording. Their voice message is posted on Twitter as their new status.
- Users can navigate to the URL again if they want to log out and stop using KooTweet.

When a user sends an SMS to **09227507512**:
- User sends SMS in any of the formats specified below.
- Based on the format, the app either tweets a new status or retrieves tweets based on username, hashtag or from home timeline.

## SMS formats
Send SMS to **09227507512** in one of the following formats:
```
kootweet {your custom message} : Updates your Twitter status to 'your message'.
Ex: kootweet KooTweet is rad :D

kootweet gettweets : Gets 4 neatly formatted tweets from your home feed

kootweet gettweets {number} : Gets the specified number of tweets from your home feed.
Ex: kootweet gettweets 3

kootweet gettweets {number} {query} : Gets the specified number of tweets with the given query.
Examples:
For username:		kootweet gettweets 3 @venturesity
For hashtag:		kootweet gettweets 3 #KooTweetApp
For general query:	kootweet gettweets 3 kookoo
```
Keep the {number} as low as possible because Kookoo cannot handle SMSs with large text. number less than 4 for testing purposes should be fine.

## Highlights of Tech used
- Using Firebase - Passwordless One Time Log-in is implemented.
	- Firebase handles both Twitter auth and Custom Phone number auth with custom generated Firebase tokens to handle all communication securely over HTTPS. HTTP is not allowed to prevent attacks.
	- Firebase naturally becomes highly scalable data structure as it uses NoSQL and tight Security Rules have been defined to prevent wrong users tweeting on behalf of someone else.
- Backend runs on Python Flask along with the concept of Blueprints to conveniently build larger applications
- For the web frontend - MaterializeCSS has been used
- Complete Twitter API integration
- Google URL Shortener to shorten URLs sent in SMSs and in tweets
- Minor attack prevention: Master key is checked using custom *constant_compare_time* function to prevent Timing Attacks to prevent Master key from getting stolen.
