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
2. CD into the directory where the server is.
3. Run the server using "python webserver.py". You should see "Server started on http://localhost:6789".
4. Open any web browser.
5. Enter the address http:/localhost:6789/HelloWorld.html". This should load the page.
6. You can test requesting other resources from that page.

## (B) proxyserver.py
Libraries used:

How to run: