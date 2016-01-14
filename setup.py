from setuptools import setup

setup(name='HackDemos',
	version='1.0',
	description='A basic Flask app for hack demos',
	author='Rakshak R.Hegde',
	author_email='rakshakhegde@gmail.com',
	url='http://www.python.org/sigs/distutils-sig/',
	install_requires=['Flask>=0.10.1',
					  'requests',
					  'requests_oauthlib',
					  'firebase-token-generator'],
)
