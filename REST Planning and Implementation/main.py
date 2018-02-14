#/***********************************************************
#* CS496 - Assignment 2 - REST Planning and Implementation
#* Author: Stephen Townsend
#* File: main.py
#* This py file is used to implement a REST api.  The api is
#* based on a marina.  There a Boats and Slips.
#* You can Add, Delete, Modify, and View.
#* URL: https://cs496-rest-townsend.appspot.com
#***********************************************************/

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import json
import os

class Boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required = True)
	type = ndb.StringProperty(required = True)
	length = ndb.IntegerProperty(required = True)
	at_sea = ndb.BooleanProperty()
	slip = ndb.IntegerProperty()
	
class MainPage(webapp2.RequestHandler):
    def get(self):
                url = '/notes'
                
		self.response.write("<b>Welcome to the Townsend Marina                          </b><br><br>")
		self.response.write("<li>       POST    {{base url}} /boats                     <br>")
		self.response.write("<li>       GET     {{base url}} /boats/{{boatID}}          <br>")
		self.response.write("<li>       GET     {{base url}} /boats                     <br>")
		self.response.write("<li>       PATCH   {{base url}} /boats/{{boatID}}          <br>")
		self.response.write("<li>       DELETE  {{base url}} /boats/{{boatID}}          <br>")
		self.response.write("<li>       DELETE  {{base url}} /boats                     <br>")
		self.response.write("<li>       POST    {{base url}} /slips                     <br>")
		self.response.write("<li>       GET     {{base url}} /slips/{{slipID}}          <br>")
		self.response.write("<li>       GET     {{base url}} /slips                     <br>")
		self.response.write("<li>       PATCH   {{base url}} /slips/{{slipID}}          <br>")
		self.response.write("<li>       DELETE  {{base url}} /slips/{{slipID}}          <br>")
		self.response.write("<li>       DELETE  {{base url}} /slips                     <br>")
		self.response.write("<li>       PUT     {{base url}} /slips/{{slipID}}/dock     <br>")
		self.response.write("<h3>       For More Information                            </h3>")
		self.response.write("<a href="+ url + ">Click here")
		
class NoteHandler(webapp2.RequestHandler):
        def get(self):
                #Create HTML Template to sub build_url variable into index.html
                path = os.path.join(os.path.dirname(__file__), 'www/index.html')
                self.response.out.write(template.render(path, 'output'))


class BoatHandler(webapp2.RequestHandler):
        #Inputs: {"name":"Name Here", "type":"Tyoe Here", "length": "Length Here"}
        #NOTE: All boats are set to at_sea as they are created
	def post(self):
		jsonData = json.loads(self.request.body)
		nameFlag = False
		typeFlag = False
		lengthFlag = False
		validFlag = True

		#Loop through the json body to verify the data.
		for jsonParse in jsonData:
			if jsonParse == "name":
                                nameFlag = True
			elif jsonParse == "type":
                                typeFlag = True
                        elif jsonParse == "length":
                                lengthFlag = True
			else:   #if there are any other inputs then it is an invalid post
                                validFlag = False
                                
		if nameFlag and typeFlag and lengthFlag and validFlag == True:
			newBoat = Boat(name=jsonData['name'], 
					type=jsonData['type'], 
					length=jsonData['length'])
			newBoat.at_sea = True
			newBoat.put()
			newBoat.id = str(newBoat.key.urlsafe())
			boat_dict = newBoat.to_dict()
			boat_dict['self'] = '/boats/' + newBoat.id
			newBoat.id = newBoat.key.urlsafe()

                        #Post auto generated id and data
                        newBoat.put()
                        
                        #Created Successful
			self.response.status = 201
			self.response.write(json.dumps(boat_dict))
			
		else:   #Json data is not valid
			self.response.status = 400
			self.response.write("Invalid request: Req: name str, type str, length int")
		
	def get(self, id = None):
                boatsData = Boat.query().fetch()
                boatExists = False
                
                if id:  #Display a single boat
                        for boatParse in boatsData:
                                if id == boatParse.key.urlsafe():
                                        boatExists = True    
                        if boatExists:
                                getBoat = ndb.Key(urlsafe=id).get()
                                getBoat_dict = getBoat.to_dict()
                                getBoat_dict['self'] = '/boats/' + id
                                self.response.status = 200
                                self.response.write(json.dumps(getBoat_dict))
                                
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The specified boat not found")
                                
		else:   #Display all boats
                        boatsDisplay = {'Boats':[]}
                        for boatParse in boatsData:
                                id = boatParse.key.urlsafe()
                                boats_dict = boatParse.to_dict()
                                boats_dict['self'] = '/boats/' + id
                                boats_dict['id'] = id
                                boatsDisplay['Boats'].append(boats_dict)
                        self.response.write(json.dumps(boatsDisplay))

	def delete(self, id = None):
                boatsData = Boat.query().fetch()
                slipsData = Slip.query().fetch()
                boatExists = False
                slipExists = False
                
		if id:  
                        for boatParse in boatsData:
                                if id == boatParse.key.urlsafe():
                                        boatExists = True
                        if boatExists:
                                for slipParse in slipsData:
                                        if boatParse.slip == slipParse.number:
                                                slipExists = True
                                if slipExists:
                                        #Extra credit to keep the slips history
                                        if slipParse.departure_history is None: #Check for any previous history
                                                slipPrevHistory = ""            #Set to a string if None
                                        else:
                                                slipPrevHistory = slipParse.departure_history   #Place previous history in a variable
                                        slipCurrHistory = "{Boat: " + boatParse.name + ", Arrival: " + slipParse.arrival_date +"}" #Combine to make history
                                        slipParse.departure_history = slipPrevHistory + slipCurrHistory #Combine previous and current into departure_history
                                        slipParse.current_boat = None   #Set current_boat to null
                                        slipParse.arrival_date = None   #Set arrival_date to null
                                        slipParse.put()                 #Set the changes with put call

                                ndb.Key(urlsafe=id).delete()    #Delete the boat
                                
                                #Success Message
                                self.response.status = 200
                                self.response.write("Success: The boat was deleted")
                                
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected boat not found")
                                
                else:   #Error Message
                        #self.response.status = 400;
                        #self.response.write("Invalid request: No id given")

                        for boatParse in boatsData:
                                id = boatParse.key.urlsafe()
                                ndb.Key(urlsafe=id).delete()

        #Inputs: {"name":"Name Here", "type":"Tyoe Here", "length": "Length Here"}
        #       Optional: add above or alone to remove a boat from slip {"at_sea": true}
        def patch(self, id = None):
                boatsData = Boat.query().fetch()
                slipsData = Slip.query().fetch()
                jsonData = json.loads(self.request.body)
                boatExists = False
                changeAtSea = True
                atSea = False
                inSlip = False
                slipExists = False
                valid = True

                if id:
                        for boatParse in boatsData:
                                if id == boatParse.key.urlsafe():
                                        boatExists = True         
                        if boatExists:
                                getBoat = ndb.Key(urlsafe=id).get()
                                for jsonParse in jsonData:
                                        if jsonParse == "name":
                                                boatParse.name = jsonData['name']
                                        elif jsonParse == "type":
                                                boatParse.type = jsonData['type']
                                        elif jsonParse == "length":
                                                boatParse.length = jsonData['length']
                                        elif jsonParse == "at_sea":
                                                #Used to check if the boat is in a slip already
                                                if boatParse.slip is None:
                                                        changeAtSea = False
                                                        if jsonData['at_sea'] == True:
                                                                atSea = True
                                                elif boatParse.slip and jsonData['at_sea'] == False:
                                                        changeAtSea = False
                                                        inSlip = True
                                                else:
                                                        boatParse.at_sea = jsonData['at_sea']
                                                        for slipParse in slipsData:
                                                                if boatParse.slip == slipParse.number:
                                                                        slipExists = True
                                                        if slipExists:
                                                                if slipParse.departure_history is None:
                                                                        slipPrevHistory = ""
                                                                else:
                                                                        slipPrevHistory = slipParse.departure_history
                                                                slipCurrHistory = "{Boat: " + boatParse.name + ", Arrival: " + slipParse.arrival_date +"}"
                                                                slipParse.departure_history = slipPrevHistory + slipCurrHistory
                                                                slipParse.current_boat = None
                                                                slipParse.arrival_date = None
                                                                boatParse.slip = None
                                                                slipParse.put()
                                        else: #There are more items than allowed in json body
                                                valid = False
                                if changeAtSea == True:
                                        if valid == True:
                                                getBoat.put()
                                                getBoat_dict = getBoat.to_dict()

                                                #Success Message
                                                self.response.status = 200
                                                self.response.write("Success: Boat data was updated")
                                        else:
                                                self.response.status = 400
                                                self.response.write("Invalid request. Use name, type, or length")
                                                
                                elif atSea == True:   #Error Message
                                        self.response.status = 400
                                        self.response.write("Error: Boat is already at sea")
                                        
                                elif inSlip == True:   #Error Message
                                        self.response.status = 400
                                        self.response.write("Error: Boat is already in slip")
                                        
                                else:   #Error Message
                                        self.response.status = 400
                                        self.response.write("Error: Boat needs to be in slip")
                                        
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected boat not found")
                                
                else:   #Error Message
                        self.response.status = 400;
                        self.response.write("Invalid request: No id given")

class Slip(ndb.Model):
        id = ndb.StringProperty()
	number = ndb.IntegerProperty(required = True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()
	departure_history = ndb.StringProperty()

                                
class SlipHandler(webapp2.RequestHandler):
        #Inputs: {"number":"Number Here"}
        #NOTE: All slips are set to empty as they are created
	def post(self):
                slipsData = Slip.query().fetch()
		jsonData = json.loads(self.request.body)
		numberFlag = False
		validFlag = True
		numberExists = False

                for jsonParse in jsonData:
                        if jsonParse == "number":
                                numberFlag = True
                        else:   #if there are any other inputs then it is an invalid post
                                valid = False
                                
                if numberFlag and validFlag == True:
                        for slipParse in slipsData:
                                if slipParse.number == jsonData['number']:
                                        numberExists = True
                        if numberExists == False:
                                newSlip = Slip(number=jsonData['number'])
                                newSlip.at_sea = True
                                newSlip.put()
                                newSlip.id = str(newSlip.key.urlsafe())
                                slip_dict = newSlip.to_dict()
                                slip_dict['self'] = '/slips/' + newSlip.id
                                newSlip.id = newSlip.key.urlsafe()

                                #Post auto generated id and data
                                newSlip.put()

                                #Created Successful
                                self.response.status = 201
                                self.response.write(json.dumps(slip_dict))

                        else:   #Error Message
                                self.response.status = 400
                                self.response.write(json.dumps("Invalid request: number already exists"))
   
                else:   #Error Message
                        self.response.status = 400
                        self.response.write(json.dumps("Invalid request: Req: number int, current_boat str, arrival_date str"))
	def get(self, id = None):
                slipsData = Slip.query().fetch()
                slipExists = False
                
                if id:  #Display a single slip
                        for slipParse in slipsData:
                                if id == slipParse.key.urlsafe():
                                        slipExists = True
                                        
                        if slipExists:
                                getSlip = ndb.Key(urlsafe=id).get()
                                getSlip_dict = getSlip.to_dict()
                                getSlip_dict['self'] = '/slips/' + id
                                self.response.status = 200
                                self.response.write(json.dumps(getSlip_dict))
                                
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The specified slip not found")
                                
		else:   #Display all slips
                        slipsDisplay = {'Slips':[]}
                        for slipParse in slipsData:
                                id = slipParse.key.urlsafe()
                                slips_dict = slipParse.to_dict()
                                slips_dict['self'] = '/slips/' + id
                                slips_dict['id'] = id
                                slipsDisplay['Slips'].append(slips_dict)
                        self.response.write(json.dumps(slipsDisplay))

	def delete(self, id = None):
                slipsData = Slip.query().fetch()
                boatsData = Boat.query().fetch()
                slipExists = False
                boatExists = False
                
		if id:
                        for slipParse in slipsData:
                                if id == slipParse.key.urlsafe():
                                        slipExists = True
                        if slipExists:
                                for boatParse in boatsData:
                                       if boatParse.id == slipParse.current_boat:
                                                boatExists = True
                                if boatExists:
                                        boatParse.at_sea = True
                                        boatParse.slip = None
                                        boatParse.put()
                                ndb.Key(urlsafe=id).delete()

                                #Success Message
                                self.response.status = 200
                                self.response.write("Success: The slip was deleted")
                                
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected slip not found")
                                
                else:   #Error Message
                        #self.response.status = 400;
                        #self.response.write("Invalid request: No id given")

                        for slipParse in slipsData:
                                id = slipParse.key.urlsafe()
                                ndb.Key(urlsafe=id).delete() 

        #Inputs: {"number":"Number Here"}
        def patch(self, id = None):
                slipsData = Slip.query().fetch()
                jsonData = json.loads(self.request.body)
                invalid = False
                slipExists = False
                numberExists = False
                
                if id:
                        for slipParse in slipsData:
                                if id == slipParse.key.urlsafe():
                                        slipExists = True
                                if slipParse.number == jsonData['number']:
                                        numberExists = True 
                        if slipExists:
                                if numberExists == False:
                                        getSlip = ndb.Key(urlsafe=id).get()
                                        for jsonParse in jsonData:
                                                if jsonParse == "number":
                                                        getSlip.number = jsonData['number']
                                                else:   #There are more items than allowed in json body
                                                        invalid = True
                                        if invalid == False:
                                                getSlip.put()
                                                getSlip_dict = getSlip.to_dict()
                                                #self.response.write(json.dumps(getSlip_dict))

                                                #Success Message
                                                self.response.status = 200
                                                self.response.write("Success: slip 'number' was updated")
                                                
                                        else:   #Error Message
                                                self.response.status = 400
                                                self.response.write("Invalid request: Check the format and only update number")

                                else:   #Error Message
                                        self.response.status = 400
                                        self.response.write(json.dumps("Invalid request: number already exists"))

                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected slip not found")
                                
                else:   #Error Message
                        self.response.status = 400;
                        self.response.write("Invalid request: No id given")


class SlipDockHandler(webapp2.RequestHandler):
	def put(self, id = None):
                slipsData = Slip.query().fetch()
                boatsData = Boat.query().fetch()
                empty = False
                slipExists = False
                boatExists = False
                boatFree = False
                invalid = False
                
                if id:
                        for slipParse in slipsData:
                                if id == slipParse.key.urlsafe():
                                        slipExists = True
                                        if slipParse.current_boat is None:
                                                empty = True
                        if slipExists:
                                if empty:
                                        putSlip = ndb.Key(urlsafe=id).get()
                                        putData = json.loads(self.request.body)

                                        for boatParse in boatsData:
                                                if boatParse.id == putData['current_boat']:
                                                        boatExists = True
                                        if boatExists:
                                                if boatParse.slip is None:
                                                        boatFree = True
                                                if boatFree:
                                                        putBoat = ndb.Key(urlsafe=boatParse.id).get()
                                                        for parse in putData:
                                                                if parse == "current_boat":
                                                                        putSlip.current_boat = putData['current_boat']
                                                                elif parse == "arrival_date":
                                                                        putSlip.arrival_date = putData['arrival_date']
                                                                else:   #if there are any other inputs then it is an invalid post
                                                                        invalid = True
                                                        if invalid == False:
                                                                putSlip.put()
                                                                putBoat.at_sea = False
                                                                putBoat.slip = putSlip.number
                                                                putBoat.put()
                                                                putSlip_dict = putSlip.to_dict()

                                                                #Created Successful
                                                                self.response.status = 201
                                                                self.response.write(json.dumps(putSlip_dict))
                                                                
                                                        else:   #Error Message
                                                                self.response.status = 400
                                                                self.response.write("Invalid request: Use current_boat and arrival_date")

                                                else:   #Error Message
                                                        self.response.status = 403
                                                        self.response.write("Forbidden: The selected boat is already in a slip")

                                        else:   #Error Message
                                                self.response.status = 404
                                                self.response.write("Error: The selected boat not found")
                                                
                                else:   #Error Message
                                        self.response.status = 403
                                        self.response.write("Forbidden: The selected slip is occupied")
                                        
                        else:   #Error Message
                                self.response.status = 404
                                self.response.write("Error: The selected slip not found")
                                

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/notes', NoteHandler),
        ('/boats', BoatHandler),
        ('/boats/(.*)', BoatHandler),
        ('/slips', SlipHandler),
        ('/slips/(.*)/dock', SlipDockHandler),
        ('/slips/(.*)', SlipHandler)
], debug=True)
