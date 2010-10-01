import wsgiref.handlers
import os
import xml.dom.minidom
import feedparser
import datetime
import time
import logging

from operator import attrgetter
from time import strftime, strptime, gmtime
from xml.dom.minidom import Node
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import urlfetch

class Feed(db.Model):
    url = db.StringProperty()
    name = db.StringProperty()
    def entries(self):
        result = urlfetch.fetch(self.url)
        logging.info("Fetched URL " + self.url)
        updates = []
        if result.status_code == 200:
            feed = feedparser.parse(result.content)
            for entry in feed['entries']:
                x = Entry()
                x.service = self.name
                x.title = entry['title']
                x.link = entry['link']
                try:
                    x.content = entry.summary
                except AttributeError:
                    x.content = entry['title']
                x.timestamp = entry.updated_parsed
                updates.append(x)
        return updates          
    def top_entries(self):
        return self.entries()[0:5]
      
class Entry:
    def __init__(self=None, title=None, link=None, timestamp=None, content=None, service=None):
        self.title = title
        self.link = link
        self.content = content
        self.service = service
        self.timestamp = timestamp
    def printTime(self):
        return strftime('%B %d,%Y at %I:%M:%S %p',self.timestamp)            

class MainPage(webapp.RequestHandler):
  def get(self):
    feed_query = Feed.all()
    feed_query.order('name')
    
    template_values = {
        'feeds': [ {'name': feed.name, 'entries': feed.top_entries() } for feed in feed_query ]
        }
    
    logging.debug("got here!")
    logging.info("got here 2")
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class InitDatabase(webapp.RequestHandler):
    def get(self):
        if Feed.all().count() == 0:
            feed = Feed()
            feed.url = "http://peter.krautzberger.info/atom.xml"
            feed.name = "thelazyscience"
            feed.put()
        self.redirect('/')
        

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage),
                                        ('/init', InitDatabase)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
