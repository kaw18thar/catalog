from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h2>Hello! <a href = '/restaurants'>Restaurants List</a> </h2> "
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += " <h2> <a href = '/hello'>Hello page</a> </h2>"
                output += "<a href = '/restaurants/new'>new restaurant</a>"
                output += " <h4> Restaurants: </h4> <ul>"
                items = session.query(Restaurant).all()
                for item in items:
                    output += "<li >%s </li>" % item.name
                    output += "<a href='/restaurants/%s/edit'> edit" % item.id
                    output += "</a><a href='/restaurants/%s/delete'> delete </a>"  % item.id
                output += "</ul>"
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id =
                    restaurantIDPath).one()
                if myRestaurantQuery != [] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1> %s" % myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantIDPath
                    output += "<input name='newRestaurantName' type='text' placeholder = '%s'" % myRestaurantQuery.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form>"
                    output += "</html></body>"
                    self.wfile.write(output)
                    print output
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id =
                restaurantIDPath).one()
                if myRestaurantQuery != [] :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h3> Are you sure you want to remove %s" % myRestaurantQuery.name
                    output += " permenantly? </h3>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/deleted'>" % restaurantIDPath
                    output += "<select name='choice'>"
                    output += "<option value='Yes'>Yes, delete it perminantly </option>"
                    output += "<option value='No'>No, I've changed my mind </option>"
                    output += "</select> <button type = 'submit'>Submit choice </button> "
                    output += "</form>"
                    output += "</html></body>"
                    self.wfile.write(output)
                    print output
        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)
            
    
    def do_POST(self):
        try:
            if self.path.endswith("/deleted"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('choice')
                    restaurantIDPath = self.path.split("/")[2]
                    if messagecontent == 'Yes':
                        restaurantToRemove = session.query(Restaurant).filter_by(id =
                            restaurantIDPath).one()
                    
                    if restaurantToRemove != [] :
                        restaurantToRemove.id = restaurantIDPath
                        session.delete(restaurantToRemove)
                        session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]
                    myRestaurantQuery = session.query(Restaurant).filter_by(id =
                        restaurantIDPath).one()
                    
                    if myRestaurantQuery != [] :
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()


            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            pass
def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print ("Web server running on port %s" %port )
        server.serve_forever()

    except KeyboardInterrupt:
        print ("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()