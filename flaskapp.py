import flask

app = flask.Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

import hacks.kookoosocialmedia
app.register_blueprint(hacks.kookoosocialmedia.app, url_prefix='/kookoosocialmedia')

@app.route('/')
def home():
	return 'App is alive!'

@app.route('/<path:resource>')
def serveStaticResource(resource):
	return flask.send_from_directory('static/', resource)

@app.route('/env/')
def env():
	import os
	response_body = ['%s: %s' % (key, value)
		for key, value in sorted(os.environ.items())]
	return '\n'.join(response_body), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
	app.run(debug=False)
