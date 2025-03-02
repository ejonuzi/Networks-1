from socket import *
import os
import threading
import time
from datetime import datetime, timezone
import mimetypes
import hashlib

class ProxyServer:
    def start(self):
        """Start the server and listen for connections."""

        # Initialize server
        self.serverHost = 'localhost'
        self.serverPort = 8888
        self.cacheDir = "proxy_cache"
        if not os.path.exists(self.cacheDir): # create cache directory if it doesn't exist
            os.makedirs(self.cacheDir)
        self.serverSocket = socket(AF_INET, SOCK_STREAM) # create TCP welcoming socket
        self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # set socket option to reuse the address
        self.serverSocket.bind((self.serverHost, self.serverPort))
        self.serverSocket.listen(10) # begin listening to incoming TCP requests
        print(f"Proxy server started on http://{self.serverHost}:{self.serverPort}")

        try:
            while True:  # loop forever
                connectionSocket, addr = self.serverSocket.accept()  # wait for incoming requests
                print(f"Connection from {addr}")

                # Handle client request in a new thread, this allows multiple clients to be handled at the same time
                clientThread = threading.Thread(target=self.handleClient, args=(connectionSocket,))
                clientThread.daemon = True
                clientThread.start()

        except KeyboardInterrupt:
            print("Server shutting down...") 
        finally:
            self.serverSocket.close() 

    def handleClient(self, clientConnection):
        """Process client request and send response."""
        try:
            # Parse request
            requestData = clientConnection.recv(4096).decode()
            if not requestData:
                return
            requestData = requestData.split('\n')
            request = requestData[0].strip()
            print(f"Received request: {request}")
            
            # Parse method and path
            try:
                method, url, version = request.split()
            except ValueError:
                self.sendErrorResponse(clientConnection, 400, "Bad Request")
                return
            
            # only handle GET requests
            if method != 'GET':
                self.sendErrorResponse(clientConnection, 405, "Only GET requests supported")
                return
            
            # handle URL appropriately
            if url.startswith('http://'): # only http supported
                self.handleProxyRequest(clientConnection, url)
            elif url.startswith('/'):
                # Convert '/www.example.com' to 'http://www.example.com'
                if not url.startswith('/http'):
                    url = 'http:/' + url
                self.handleProxyRequest(clientConnection, url)
            else:
                self.sendErrorResponse(clientConnection, 400, "Bad Request")

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            clientConnection.close()  # close connection to this client

    def handleProxyRequest(self, clientConnection, url):
        """Handle HTTP proxy request."""
        try:
            # Generate cache filename based on the URL
            urlHash = hashlib.md5(url.encode()).hexdigest() # use hash to convert into a fixed length that is safe to use as a file name
            cacheFile = os.path.join(self.cacheDir, urlHash)
            
            # Check if the page is cached and recent (less than 5 minutes old)
            if os.path.exists(cacheFile) and (time.time() - os.path.getmtime(cacheFile) < 300):
                print(f"Serving from cache: {url}")
                with open(cacheFile, 'rb') as f:
                    content = f.read()
                
                # get content type
                contentType, _ = mimetypes.guess_type(url)
                if contentType is None:
                    contentType = 'application/octet-stream'

                # send cached content
                self.sendResponse(clientConnection, 200, "OK", content, contentType)
                return
            
            host, path = self.parseUrl(url) # Parse URL
             
            port = 80 # use default http port to connect to web server
            
            # create socket and connect to web server
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.settimeout(5)  # 5 seconds timeout
            serverSocket.connect((host, port))
            
            # Build the request to send to the web server
            requestHeader = f"GET {path} HTTP/1.1\r\n"
            requestHeader += f"Host: {host}\r\n"
            requestHeader += "Connection: close\r\n"
            requestHeader += "User-Agent: Elnors-Proxy/1.0\r\n"
            requestHeader += "\r\n"
            
            # Send the request to the web server
            serverSocket.sendall(requestHeader.encode())
            
            # Receive response from web server
            response = b'' # bytes literal, since we're working with a network response
            while True:
                data = serverSocket.recv(4096)
                if not data:
                    break
                response += data
            
            serverSocket.close() # close connection to web server
            
            # Cache response
            with open(cacheFile, 'wb') as f:
                f.write(response)
            
            # Send response to client
            clientConnection.sendall(response)
            print(f"Request completed: {url}")
            
        except timeout:
            self.sendErrorResponse(clientConnection, 504, "Gateway Timeout")

        except error as e:
            self.sendErrorResponse(clientConnection, 502, f"Bad Gateway: {str(e)}")

        except Exception as e:
            self.sendErrorResponse(clientConnection, 500, f"Internal Server Error: {str(e)}")

    def sendResponse(self, clientConnection, statusCode, statusMessage, content, contentType):
        """Create and send an HTTP response with the content."""
        
        # Response headers
        headers = [
            f"HTTP/1.1 {statusCode} {statusMessage}",
            f"Date: {self.getDate()}",
            f"Server: PythonProxyServer/1.0",
            f"Content-Length: {len(content)}",
            f"Content-Type: {contentType}",
            "Connection: close"
        ]
        
        # Send headers and content
        response = '\r\n'.join(headers) + '\r\n\r\n'
        clientConnection.sendall(response.encode())
        clientConnection.sendall(content)

    def sendErrorResponse(self, clientConnection, statusCode, statusMessage):
        """Send an HTTP error response."""
        errorContent = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{statusCode} {statusMessage}</title>
        </head>
        <body>
            <h1>{statusCode} {statusMessage}</h1>
            <p>Error occurred while processing your request.</p>
        </body>
        </html>
        """
        
        self.sendResponse(clientConnection, statusCode, statusMessage, errorContent.encode(), "text/html")
    
    def parseUrl(self, url):
        """Parse the host and path from a url"""
        if "://" in url: # find the start of the path
            url = url.split("://", 1)[1]  # remove scheme
        host, _, rest = url.partition("/")  # split at the first slash
        path = "/" + rest if rest else "/" # extract path
        if "?" in path: # get query
            path, _, query = path.partition("?")  # split path and query
            path += "?" + query  # reconstruct full path with query if exists
        return host, path

    def getDate(self):
        """Return current date in HTTP date format."""
        now = datetime.now(timezone.utc)
        return now.strftime('%a, %d %b %Y %H:%M:%S GMT')

if __name__ == "__main__":
    proxy = ProxyServer()
    proxy.start()