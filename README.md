## Networks-1
Socket programming for TCP connections in Python

## (A) webserver.py
Libraries used:
socket - for socket programming
os - for checking if a file exists
datetime - for obtaining the current date to be used in HTTP response
mimetypes - for obtaining the content type of a file to be used in HTTP response 

How to run:
1. Open command prompt.
2. CD into the directory where webserver.py is.
3. Run the server using "python webserver.py". You should see "Server started on http://localhost:6789".
4. Open any web browser.
5. You can request the HelloWorld.html from the webserver by entering the address "http:/localhost:6789/HelloWorld.html" in your browser.
6. You can also request sample.png and sample.txt using the same method.

## (B) proxyserver.py
Libraries used:
socket - for socket programming
os - for checking if a file exists
datetime - for obtaining the current date to be used in HTTP response
mimetypes - for obtaining the content type of a file to be used in HTTP response 
threading - for handling multiple requests at the same time in separate threads
hashlib - for hashing urls into a fixed length string that is safe to use as a file name

How to run:
1. Open command prompt.
2. CD into the directory where proxyserver.py is.
3. Run The server using "python proxyserver.py" You should see "Proxy server started on http://localhost:8888".
4. Open any web browser.
5. Find any HTTP website you'd like (HTTPS is not supported).
6. Request the website through the proxy server by entering "http://localhost:8888/url" where 'url' is the url of the http site (e.g. http://www.example.com)