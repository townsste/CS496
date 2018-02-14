URL: https://cs496-rest-townsend.appspot.com

Plan out a REST URL structure and implement a working example of it which you will prove works by writing tests for it in 
much the same way as you did for GitHub. It will be up to you to decide on the appropriate URLs to use to access information.

Supported functions
Your API should support the following

All operations on Boats and Slips
Add
All newly created boats should start "At sea"
All newly created slips should be empty
Delete
Deleting a ship should empty the slip the boat was previously in
The behavior of the history of deleted boats (in the extra credit option) is undefined
Deleting a pier a boat is currently in should set that boat to be "At sea"
Modify
View
You should be able to either view a single entity or the entire collections of entities, for example, I should be able to view the details of a single boat as well as get a list of all boats
It should be possible, via a url, to view the specific boat currently occupying any slip.
Setting a boat to be "At sea"
This should cause the previously occupied slip to become empty
If you are doing the extra credit portion, this should cause the ship departure to be added to the slip history
Setting the ship to be "At sea" and updating the slip status should happen via a single API call
Managing a boat arrival
A ship should be able to arrive and be assigned a slip number
If the slip is occupied the server should return an Error 403 Forbidden message
This will require knowing the slip, date of arrival and boat
