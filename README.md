 * app.py file :
--> In this file there 10 faqs for dell company and the routes register,login,chat,logout.
--> For register you need to pass username and password in the arguments
--> Register route : once the new user is registered it displayes user registered successfully and if user is present in the mongodb it displays user already exists.
--> Login route : For this you need to pass username and password in the body in the form of JSON. Once the correct credentials are given then in postman it displays logged in successfully.
                  If wrong credentials are given then it displays Unauthorized.
--> Chat route : For this you need to pass FAQ's i.e message in the body in JSON format in postman. Once the predefined message(FAQ) is passed it gives you the response for your query.
--> Logout route : For this you just need to hit the post method, it displays with logout successfully.

* Once the app.py file is setup :
--> Open terminal and create 3 separate docker containers for python,mongodb,redis
--> Once the containers are created, then run the python container

*Commands to create containers and run the containers 
 --> docker run -itd --name python_layer -p 4002:4002 python --> to create python container
 --> docker run -itd --name mongo_layer -p 1000:27017 mongo --> to create mongo container
 --> docker run -itd --name redis_layer -p 2000:6379 redis --> to create redis container

 --> docker exec -it python_layer bash  --> to run python container
 --> After running the above python container, it will be redirected to bash directory. There you need to open a new vi file and insert the code from the app.py
 --> If the vi command doesn't work, try below commands

 --> apt-get update    |_____ These 2 commands will install vim
 --> apt install vim   |

 --> Now follow this command to open new vi file
 --> vi app.py
 --> IP Addresses: Ensure that the IP addresses for MongoDB and Redis in the app.py file match the IP addresses of your Docker containers.
 --> Port Mapping: Adjust the port mappings if necessary, depending on your local setup and Docker configuration.

--> Then after all these steps, run the final command in the same bash directory
--> python app.py
 
