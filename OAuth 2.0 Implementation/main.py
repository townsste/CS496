#/***********************************************************
#* CS496 - Assignment 3 - OAuth 2.0 Implementation
#* Author: Stephen Townsend
#* File: main.py
#* This py file is used to implement OAuth 2.0.  The will
#* rquest access to the users google+ account information using
#* the google+ api.
#* This program will redirect the user to googles authentication
#* Servers.  Once authenticated, this will use the return token
#* to display their First Name, Last Name, Google+ URL, and
#* the state that was used to get the rquest.
#* URL: https://cs496-oauth-2-townsend.appspot.com
#***********************************************************/

import webapp2
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
import os
import urllib
import json
import random
import string

#Global Constants from API Credentials
CLIENT_ID = "962926920531-4dajnriqkr2nr8qqfg8j2ebuidqrtu56.apps.googleusercontent.com"
CLIENT_SECRET = "WKB74onORDYmIA333KD9aOGw"
REDIRECT_URI = "https://cs496-oauth-2-townsend.appspot.com/oauth"

#local Testing
#CLIENT_ID = "962926920531-8pe5rruav9ueuv4m2iabu01eat2s7k6d.apps.googleusercontent.com"
#CLIENT_SECRET = "omP7ZXXUUPvKFF41_bYg6DHi"
#REDIRECT_URI = "http://localhost:8080/oauth"
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        url = "https://accounts.google.com/o/oauth2/v2/auth"
        response_type = "response_type=code"
        scope = "scope=email"

#Random Generator for state 
#######################
        state = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
#######################
#Source https://pythontips.com/2013/07/28/generating-a-random-string/

        build_url = url + "?" + response_type + "&client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&" + scope + "&state=" + state
                        
        #Create HTML Template to sub build_url variable into index.html
        index = {'build_url': build_url}
        path = os.path.join(os.path.dirname(__file__), 'www/index.html')
        self.response.out.write(template.render(path, index))

	
class oauthHandler(webapp2.RequestHandler):
    def get(self):

        authCode = self.request.GET['code']
        state = self.request.GET['state']

        reqData = {'code': authCode,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'grant_type': 'authorization_code'}
                        
#This section is from Googles documentation about using urlfetch
#####################################################################
        form_data = urllib.urlencode(reqData)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url='https://www.googleapis.com/oauth2/v4/token',
            payload=form_data,
            method=urlfetch.POST,
            headers=headers)
        #self.response.write(result.content)
#####################################################################
#Source https://cloud.google.com/appengine/docs/standard/python/issue-requests

#Information for a POST Request
#POST https://www.googleapis.com/oauth2/v4/token
#code:[access-code]
#client_id:[your-client-id]
#client_secret:[your-client-secret]
#redirect_uri:[location-of-redirect-url]
#grant_type:authorization_code


        jsonData = json.loads(result.content)
        token = jsonData['access_token']    #Get the token from returned json

        #Get Request using token to access google+ account information
        #Based on above google documentation for urlfetch
        headers = {'Authorization': 'Bearer '+ token}
        result = urlfetch.fetch(
            url='https://www.googleapis.com/plus/v1/people/me',
            method=urlfetch.GET,
            headers=headers)

        jsonData = json.loads(result.content)

#Found out that if there is no account then there will be no name or URL.
#To prevent any 500 errors will need to check for this.

        urlFlag = False

        #Get required data from returned json
        if jsonData['name']['givenName']:
            fname = jsonData['name']['givenName']
        else:
            fname = "No First Name Found"

        if jsonData['name']['familyName']:
            lname = jsonData['name']['familyName']
        else:
            lname = "No Last Name Found"

        #If there is no account then there will be no url.
        #Checking json and flagging if needed
        for jsonParse in jsonData:
            if jsonParse == 'url':
                urlFlag = True 

        if urlFlag == True:
            url = jsonData['url']
            noURL = ""
        else:
            noURL = "Cannot find a URL"
            url = ""
 
        #Create HTML Template to sub variables into oauth.html
        oauth = {'fname': fname, 'lname': lname, 'url': url, 'noURL': noURL, 'state': state}
        path = os.path.join(os.path.dirname(__file__), 'www/oauth.html')
        self.response.out.write(template.render(path, oauth))

app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/oauth', oauthHandler)
], debug=True)
