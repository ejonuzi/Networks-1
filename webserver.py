from socket import *
import os
from datetime import datetime, timezone
import mimetypes

class TCPServer:
    def start(self):
        """Start the server and listen for connections."""

        # Initialize server
        self.serverHost = 'localhost'
        self.serverPort = 6789
        self.serverSocket = socket(AF_INET, SOCK_STREAM) # create TCP welcoming socket
        self.serverSocket.bind(('localhost', self.serverPort))
        self.serverSocket.listen(1) # begin listening to incoming TCP requests
        print(f"Server started on http://{self.serverHost}:{self.serverPort}")

        try:
            while True: # loop forever
                connectionSocket, addr = self.serverSocket.accept() # wait for incoming requests
                print(f"Connection from {addr}")
                try:
                    self.handleClient(connectionSocket) # handle one client at a time
                except Exception as e:
                    print(f"Error handling client: {e}")
                finally:
                    connectionSocket.close() # close connection to this client
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.serverSocket.close()

    def handleClient(self, clientConnection):
        """Process client request and send response."""
        
        # Parse request
        requestData = clientConnection.recv(1024).decode()
        if not requestData:
            return
        requestData = requestData.split('\n')
        request = requestData[0].strip()
        print(f"Recieved request: {request}")
        
        # Parse method and path
        try:
            method, path, version = request.split()
        except ValueError:
            self.sendErrorResponse(clientConnection, 400, "Bad Request")
            return
        
        # only handle GET requests since the client will only be able to request files from the server
        if method != 'GET':
            self.sendErrorResponse(clientConnection, 405, "Only GET requests supported")
            return
        
        # Fix path url
        if path == '/':
            path = '/HelloWorld.html'
        localPath = path[1:] if path.startswith('/') else path
        
        # check if file exists
        if not os.path.exists(localPath):
            self.sendErrorResponse(clientConnection, 404, "Not Found")
            return
        
        # read and send file content
        try:
            with open(localPath, 'rb') as file:
                content = file.read()
            self.sendResponse(clientConnection, 200, "OK", content, localPath)
        except Exception as e:
            print(f"Error reading file: {e}")
            self.sendErrorResponse(clientConnection, 500, "Internal Server Error")

    def sendResponse(self, clientConnection, statusCode, statusMessage, content, filePath):
        """Create and send an HTTP response with the file content."""

        # get content type
        contentType, _ = mimetypes.guess_type(filePath)
        if contentType is None:
            contentType = 'application/octet-stream'
        
        # response headers
        headers = [
            f"HTTP/1.1 {statusCode} {statusMessage}",
            f"Date: {self.getDate()}",
            f"Server: PythonHTTPServer/1.0",
            f"Content-Length: {len(content)}",
            f"Content-Type: {contentType}",
            "Connection: close"
        ]
        
        # send headers and content
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
        
        self.sendResponse(clientConnection, statusCode, statusMessage, errorContent.encode(), "error.html")
    
    def getDate (self):
        """Return current date in HTTP date format."""
        now = datetime.now(timezone.utc)
        return now.strftime('%a, %d %b %Y %H:%M:%S GMT')

if __name__ == "__main__":
    server = TCPServer()
    server.start()