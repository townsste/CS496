URL: https://cs496-oauth-2-townsend.appspot.com

Implement a OAuth 2.0 Server Side flow without using a 3rd party OAuth library. 
it can access protected resources on the users Google+ account.

Implement the following pieces of functionality:

A page that has a link a user clicks to visit the Google OAuth 2.0 endpoint
A page that handles the user getting redirect back to your website from Google's endpoint and handles the exchanging of the access code for a token
A page (which could use the same handler as the page they were redirected to) which uses that token to access and display  the following information: The users first and last name and the URL to access their Google Plus account. It should also print out the value of the state variable that was used to secure the original redirect.
The only scope you are allowed to request is "email".
