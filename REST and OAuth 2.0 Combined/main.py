#/***********************************************************
#* CS496 - Final Project
#* Author: Stephen Townsend
#* File: main.py
#* This py file is used to implement a REST api.  The api is
#* based on a property management company.  There a Tenants and Properties.
#* You can Add, Delete, Modify, and View.
#* URL: https://cs496-rest-final-townsend.appspot.com
#***********************************************************/

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
import json
import os
import urllib
import random
import string


#Global Constants from API Credentials
CLIENT_ID = "70593947786-hp6jnbbioonnevabcafergtlj5i7h3k8.apps.googleusercontent.com"
CLIENT_SECRET = "tvqyQ6GNxVumwP31voGis-kC"
REDIRECT_URI = "https://cs496-rest-final-townsend.appspot.com/oauth"

#local Testing
#CLIENT_ID = "70593947786-95o243o2psnaru7k33402l9amp681196.apps.googleusercontent.com"
#CLIENT_SECRET = "zmkxKJL6X2haOs778Wey0cGy"
#REDIRECT_URI = "http://localhost:8080/oauth"

class MainPage(webapp2.RequestHandler):
    def get(self):
        url = '/notes'
        
        self.response.write("<h1>Welcome to the Townsend Property Management                          </h1><br><br>")
        self.response.write("<li>       POST    {{base url}} /tenants                     <br>")
        self.response.write("<li>       GET     {{base url}} /tenants/{{tenantID}}          <br>")
        self.response.write("<li>       GET     {{base url}} /tenants                     <br>")
        self.response.write("<li>       PATCH   {{base url}} /tenants/{{tenantID}}          <br>")
        self.response.write("<li>       DELETE  {{base url}} /tenants/{{tenantID}}          <br>")
        self.response.write("<li>       DELETE  {{base url}} /tenants                     <br>")
        self.response.write("<li>       POST    {{base url}} /properties                     <br>")
        self.response.write("<li>       GET     {{base url}} /properties/{{propertyID}}          <br>")
        self.response.write("<li>       GET     {{base url}} /properties                     <br>")
        self.response.write("<li>       PATCH   {{base url}} /properties/{{propertyID}}          <br>")
        self.response.write("<li>       DELETE  {{base url}} /properties/{{propertyID}}          <br>")
        self.response.write("<li>       DELETE  {{base url}} /properties                     <br>")
        self.response.write("<li>       PUT     {{base url}} /properties/{{propertyID}}/move     <br>")
        self.response.write("<h3>       For More Information                            </h3>")
        self.response.write("<a href="+ url + ">Click here""</a>")



        authUrl = "https://accounts.google.com/o/oauth2/v2/auth"
        response_type = "response_type=code"
        scope = "scope=email"

#Random Generator for state 
#######################
        state = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
#######################
#Source https://pythontips.com/2013/07/28/generating-a-random-string/

        build_url = authUrl + "?" + response_type + "&client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URI + "&" + scope + "&state=" + state
                        
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
        
        #Create HTML Template to sub variables into oauth.html
        oauth = {'token': token,}
        path = os.path.join(os.path.dirname(__file__), 'www/oauth.html')
        self.response.out.write(template.render(path, oauth))

class NoteHandler(webapp2.RequestHandler):
    def get(self):
        #Create HTML Template to sub build_url variable into index.html
        path = os.path.join(os.path.dirname(__file__), 'www/notes.html')
        self.response.out.write(template.render(path, 'output'))

class Tenant(ndb.Model):
    id = ndb.StringProperty()
    userID = ndb.StringProperty()
    firstName = ndb.StringProperty(required = True)
    lastName = ndb.StringProperty(required = True)
    pet = ndb.BooleanProperty(required = True)
    available = ndb.BooleanProperty()
    property = ndb.StringProperty()

class TenantHandler(webapp2.RequestHandler):
        #Inputs: {"firstName":"First Name Here", "lastName":"Last Name Here", "pet": "Pet Here"}
        #NOTE: All tenants are set to available as they are created
	def post(self):
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                    if jsonParse == "error":
                            validToken = False

            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
            
                jsonData = json.loads(self.request.body)
                firstNameFlag = False
                lastNameFlag = False
                petFlag = False
                validFlag = True

                #Loop through the json body to verify the data.
                for jsonParse in jsonData:
                        if jsonParse == "firstName":
                                firstNameFlag = True
                        elif jsonParse == "lastName":
                                lastNameFlag = True
                        elif jsonParse == "pet":
                                petFlag = True
                        else:   #if there are any other inputs then it is an invalid post
                                validFlag = False
                                
                if firstNameFlag and lastNameFlag and petFlag and validFlag == True:
                    newTenant = Tenant(firstName=jsonData['firstName'], 
                                        lastName=jsonData['lastName'], 
                                        pet=jsonData['pet'],
                                        userID=authUser)
                    newTenant.available = True
                    newTenant.put()
                    newTenant.id = str(newTenant.key.urlsafe())
                    tenant_dict = newTenant.to_dict()
                    tenant_dict['self'] = '/tenants/' + newTenant.id
                    newTenant.id = newTenant.key.urlsafe()

                    #Post auto generated id and data
                    newTenant.put()
                    
                    #Created Successful
                    self.response.status = 201
                    self.response.write(json.dumps(tenant_dict))
                        
                else:   #Json data is not valid
                    self.response.status = 400
                    self.response.write("Invalid request: Req: firstName str, lastName str, pet int")
            else:
                    self.response.status = 401
                    self.response.write("Unauthorized: Bad Token")
		
	def get(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
                    
                tenantsData = Tenant.query().fetch()
                tenantExists = False
                        
                if id:  #Display a single tenant
                    for tenantParse in tenantsData:
                        if id == tenantParse.key.urlsafe():
                            if tenantParse.userID == authUser:
                                tenantExists = True    
                    if tenantExists:
                        getTenant = ndb.Key(urlsafe=id).get()
                        getTenant_dict = getTenant.to_dict()
                        getTenant_dict['self'] = '/tenants/' + id
                        self.response.status = 200
                        self.response.write(json.dumps(getTenant_dict))
                            
                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The specified tenant not found")
                                
                else:   #Display all tenants
                    tenantsDisplay = {'Tenants':[]}
                    for tenantParse in tenantsData:
                        if tenantParse.userID == authUser:
                            id = tenantParse.key.urlsafe()
                            tenants_dict = tenantParse.to_dict()
                            tenants_dict['self'] = '/tenants/' + id
                            tenants_dict['id'] = id
                            tenantsDisplay['Tenants'].append(tenants_dict)
                    self.response.write(json.dumps(tenantsDisplay))
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")

	def delete(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}

            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                    if jsonParse == "error":
                            validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
                    
                tenantsData = Tenant.query().fetch()
                propertiesData = Property.query().fetch()
                tenantExists = False
                propertyExists = False
                
                if id:  
                    for tenantParse in tenantsData:
                        if id == tenantParse.key.urlsafe():
                            if tenantParse.userID == authUser:
                                tenantExists = True
                    if tenantExists:
                        for propertyParse in propertiesData:
                            if tenantParse.property == propertyParse.address:
                                propertyExists = True
                        if propertyExists:
                            #Extra credit to keep the properties history
                            if propertyParse.tenant_history is None: #Check for any previous history
                                propertyPrevHistory = ""            #Set to a string if None
                            else:
                                propertyPrevHistory = propertyParse.tenant_history   #Place previous history in a variable
                            propertyCurrHistory = "{Tenant: " + propertyParse.current_tenant +"}" #Combine to make history
                            propertyParse.tenant_history = propertyPrevHistory + propertyCurrHistory #Combine previous and current into tenant_history
                            propertyParse.current_tenant = None   #Set current_tenant to null
                            propertyParse.put()                 #Set the changes with put call

                        ndb.Key(urlsafe=id).delete()    #Delete the tenant
                        
                        #Success Message
                        self.response.status = 200
                        self.response.write("Success: The tenant was deleted")
                            
                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The selected tenant not found")
                                
                else:   #Error Message
                    #self.response.status = 400;
                    #self.response.write("Invalid request: No id given")

                    for tenantParse in tenantsData:
                        if tenantParse.userID == authUser:
                            id = tenantParse.key.urlsafe()
                            ndb.Key(urlsafe=id).delete()
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")

        #Inputs: {"firstName":"First Name Here", "lastName":"Last Name Here", "pet": "Pet Here"}
        #       Optional: add above or alone to remove a tenant from property {"available": true}
        def patch(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
                    
                tenantsData = Tenant.query().fetch()
                propertiesData = Property.query().fetch()
                jsonData = json.loads(self.request.body)
                tenantExists = False
                changeAvailable = True
                available = False
                inProperty = False
                propertyExists = False
                valid = True

                if id:
                    for tenantParse in tenantsData:
                        if id == tenantParse.key.urlsafe():
                            if tenantParse.userID == authUser:
                                tenantExists = True         
                    if tenantExists:
                        getTenant = ndb.Key(urlsafe=id).get()
                        for jsonParse in jsonData:
                            if jsonParse == "firstName":
                                tenantParse.firstName = jsonData['firstName']
                            elif jsonParse == "lastName":
                                tenantParse.lastName = jsonData['lastName']
                            elif jsonParse == "pet":
                                tenantParse.pet = jsonData['pet']
                            elif jsonParse == "available":
                                #Used to check if the tenant is in a property already
                                if tenantParse.property is None:
                                    changeAvailable = False
                                    if jsonData['available'] == True:
                                        available = True
                                elif tenantParse.property and jsonData['available'] == False:
                                    changeAvailable = False
                                    inProperty = True
                                else:
                                    tenantParse.available = jsonData['available']
                                    for propertyParse in propertiesData:
                                        if tenantParse.property == propertyParse.address:
                                                propertyExists = True
                                    if propertyExists:
                                        if propertyParse.tenant_history is None:
                                            propertyPrevHistory = ""
                                        else:
                                            propertyPrevHistory = propertyParse.tenant_history
                                            propertyCurrHistory = "{Tenant: " + propertyParse.current_tenant +"}" #Combine to make history
                                            propertyParse.tenant_history = propertyPrevHistory + propertyCurrHistory
                                            propertyParse.current_tenant = None
                                            tenantParse.property = None
                                            propertyParse.put()
                            else: #There are more items than allowed in json body
                                    valid = False
                        if changeAvailable == True:
                            if valid == True:
                                getTenant.put()
                                getTenant_dict = getTenant.to_dict()

                                #Success Message
                                self.response.status = 200
                                self.response.write("Success: Tenant data was updated")
                            else:
                                self.response.status = 400
                                self.response.write("Invalid request. Use firstName, lastName, or pet")
                                        
                        elif available == True:   #Error Message
                                self.response.status = 400
                                self.response.write("Error: Tenant is already available")
                        
                        elif inProperty == True:   #Error Message
                                self.response.status = 400
                                self.response.write("Error: Tenant is already in property")
                                
                        else:   #Error Message
                                self.response.status = 400
                                self.response.write("Error: Tenant needs to be in property")
                                    
                    else:   #Error Message
                            self.response.status = 404
                            self.response.write("Error: The selected tenant not found")
                                
                else:   #Error Message
                        self.response.status = 400;
                        self.response.write("Invalid request: No id given")
            else:
                    self.response.status = 401
                    self.response.write("Unauthorized: Bad Token")

class Property(ndb.Model):
    id = ndb.StringProperty()
    userID = ndb.StringProperty()
    address = ndb.StringProperty(required = True)
    bed = ndb.IntegerProperty(required = True)
    bath = ndb.IntegerProperty(required = True)
    rent = ndb.IntegerProperty(required = True)
    current_tenant = ndb.StringProperty()
    tenant_history = ndb.StringProperty()

class PropertyHandler(webapp2.RequestHandler):
        #Inputs: {"address":"Address Here"}
        #NOTE: All properties are set to empty as they are created
	def post(self):
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False

            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
            
                propertiesData = Property.query().fetch()
		jsonData = json.loads(self.request.body)
		addressFlag = False
		bedFlag = False
		bathFlag = False
		rentFlag = False
		validFlag = True
		addressExists = False

		for jsonParse in jsonData:
                    if jsonParse == "address":
                        addressFlag = True
                    elif jsonParse == "bed":
                        bedFlag = True
                    elif jsonParse == "bath":
                        bathFlag = True
                    elif jsonParse == "rent":
                        rentFlag = True
                    else:   #if there are any other inputs then it is an invalid post
                        validFlag = False
                                
                if addressFlag and bedFlag and bathFlag and rentFlag and validFlag == True:
                    for propertyParse in propertiesData:
                        if propertyParse.address == jsonData['address']:
                            addressExists = True
                    if addressExists == False:
                        newProperty = Property(address=jsonData['address'],
                                               bed=jsonData['bed'],
                                               bath=jsonData['bath'],
                                               rent=jsonData['rent'],
                                               userID=authUser)
                        newProperty.available = True
                        newProperty.put()
                        newProperty.id = str(newProperty.key.urlsafe())
                        property_dict = newProperty.to_dict()
                        #Test Taking out
                        #property_dict['self'] = '/properties/' + newProperty.id
                        newProperty.id = newProperty.key.urlsafe()

                        #Post auto generated id and data
                        newProperty.put()

                        #Created Successful
                        self.response.status = 201
                        self.response.write(json.dumps(property_dict))

                    else:   #Error Message
                        self.response.status = 400
                        self.response.write(json.dumps("Invalid request: address already exists"))
   
                else:   #Error Message
                    self.response.status = 400
                    self.response.write(json.dumps("Invalid request: Req: address str, bed int, bath int, rent int, current_tenant str"))

	def get(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
                    
                propertiesData = Property.query().fetch()
                propertyExists = False
                
                if id:  #Display a single property
                    for propertyParse in propertiesData:
                        if id == propertyParse.key.urlsafe():
                            if propertyParse.userID == authUser:
                                propertyExists = True 
                    if propertyExists:
                        getProperty = ndb.Key(urlsafe=id).get()
                        getProperty_dict = getProperty.to_dict()
                        getProperty_dict['self'] = '/properties/' + id
                        self.response.status = 200
                        self.response.write(json.dumps(getProperty_dict))
                            
                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The specified property not found")
                                
                else:   #Display all properties
                    propertiesDisplay = {'Properties':[]}
                    for propertyParse in propertiesData:
                        if propertyParse.userID == authUser:
                            id = propertyParse.key.urlsafe()
                            properties_dict = propertyParse.to_dict()
                            properties_dict['self'] = '/properties/' + id
                            properties_dict['id'] = id
                            propertiesDisplay['Properties'].append(properties_dict)
                    self.response.write(json.dumps(propertiesDisplay))
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")

	def delete(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
                    
                propertiesData = Property.query().fetch()
                tenantsData = Tenant.query().fetch()
                propertyExists = False
                tenantExists = False
                
		if id:
                    for propertyParse in propertiesData:
                        if id == propertyParse.key.urlsafe():
                            if propertyParse.userID == authUser:
                                propertyExists = True
                    if propertyExists:
                        for tenantParse in tenantsData:
                           if tenantParse.id == propertyParse.current_tenant:
                                tenantExists = True
                        if tenantExists:
                            tenantParse.available = True
                            tenantParse.property = None
                            tenantParse.put()
                        ndb.Key(urlsafe=id).delete()

                        #Success Message
                        self.response.status = 200
                        self.response.write("Success: The property was deleted")
                            
                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The selected property not found")
                                
                else:   #Error Message
                    #self.response.status = 400;
                    #self.response.write("Invalid request: No id given")

                    for propertyParse in propertiesData:
                        id = propertyParse.key.urlsafe()
                        ndb.Key(urlsafe=id).delete() 
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")
                
        #Inputs: {"address":"Address Here"}
        def patch(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
            
                propertiesData = Property.query().fetch()
                jsonData = json.loads(self.request.body)
                invalid = False
                propertyExists = False
                addressExists = False
                
                if id:
                    for propertyParse in propertiesData:
                        if id == propertyParse.key.urlsafe():
                            if propertyParse.userID == authUser:
                                propertyExists = True
                        if propertyParse.address == jsonData['address']:
                            addressExists = True 
                    if propertyExists:
                        if addressExists == False:
                            getProperty = ndb.Key(urlsafe=id).get()
                            for jsonParse in jsonData:
                                if jsonParse == "address":
                                    getProperty.address = jsonData['address']
                                elif jsonParse == "bed":
                                    getProperty.bed = jsonData['bed']
                                elif jsonParse == "bath":
                                    getProperty.bath = jsonData['bath']
                                elif jsonParse == "rent":
                                    getProperty.rent = jsonData['rent']
                                else:   #There are more items than allowed in json body
                                    invalid = True
                            if invalid == False:
                                getProperty.put()
                                getProperty_dict = getProperty.to_dict()
                                #self.response.write(json.dumps(getProperty_dict))

                                #Success Message
                                self.response.status = 200
                                self.response.write("Success: property 'address' was updated")
                                    
                            else:   #Error Message
                                self.response.status = 400
                                self.response.write("Invalid request: Check the format and only update address")

                        else:   #Error Message
                            self.response.status = 400
                            self.response.write(json.dumps("Invalid request: address already exists"))

                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The selected property not found")
                                
                else:   #Error Message
                    self.response.status = 400;
                    self.response.write("Invalid request: No id given")
                    
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")


class PropertyMoveHandler(webapp2.RequestHandler):
	def put(self, id = None):
            authUser = 0
            userExists = False
            validToken = True
            
            headers = {'Authorization': self.request.headers['Authorization']}
    
            result = urlfetch.fetch(
                url='https://www.googleapis.com/plus/v1/people/me',
                method=urlfetch.GET,
                headers=headers)

            jsonData = json.loads(result.content)

            for jsonParse in jsonData:
                if jsonParse == "error":
                    validToken = False
            if validToken == True:
                try:
                    authUser = jsonData['id']
                except KeyError:
                    self.response.status = 401
                    self.response.write("Unauthorized: Token expired")
            
                propertiesData = Property.query().fetch()
                tenantsData = Tenant.query().fetch()
                empty = False
                propertyExists = False
                tenantExists = False
                tenantFree = False
                invalid = False
                
                if id:
                    for propertyParse in propertiesData:
                        if id == propertyParse.key.urlsafe():
                            if propertyParse.userID == authUser:
                                propertyExists = True
                                if propertyParse.current_tenant is None:
                                    empty = True
                    if propertyExists:
                        if empty:
                            putProperty = ndb.Key(urlsafe=id).get()
                            putData = json.loads(self.request.body)

                            for tenantParse in tenantsData:
                                if tenantParse.id == putData['current_tenant']:
                                    tenantExists = True
                            if tenantExists:
                                if tenantParse.property is None:
                                    tenantFree = True
                                if tenantFree:
                                    putTenant = ndb.Key(urlsafe=tenantParse.id).get()
                                    for parse in putData:
                                        if parse == "current_tenant":
                                            putProperty.current_tenant = putTenant.firstName + " " + putTenant.lastName
                                        else:   #if there are any other inputs then it is an invalid put
                                            invalid = True
                                    if invalid == False:
                                        putProperty.put()
                                        putTenant.available = False
                                        putTenant.property = putProperty.address
                                        putTenant.put()
                                        putProperty_dict = putProperty.to_dict()

                                        #Created Successful
                                        self.response.status = 201
                                        self.response.write(json.dumps(putProperty_dict))
                                            
                                    else:   #Error Message
                                        self.response.status = 400
                                        self.response.write("Invalid request: Use current_tenant and rent")

                                else:   #Error Message
                                    self.response.status = 403
                                    self.response.write("Forbidden: The selected tenant is already in a property")

                            else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected tenant not found")
                                            
                        else:   #Error Message
                            self.response.status = 403
                            self.response.write("Forbidden: The selected property is occupied")
                                    
                    else:   #Error Message
                        self.response.status = 404
                        self.response.write("Error: The selected property not found")
            else:
                self.response.status = 401
                self.response.write("Unauthorized: Bad Token")
                                

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/notes', NoteHandler),
        ('/oauth', oauthHandler),
        ('/tenants', TenantHandler),
        ('/tenants/(.*)', TenantHandler),
        ('/properties', PropertyHandler),
        ('/properties/(.*)/move', PropertyMoveHandler),
        ('/properties/(.*)', PropertyHandler)
], debug=True)
