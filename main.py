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
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue


class Feed(db.Model):
    url = db.StringProperty()
    title = db.StringProperty()
    person = db.StringProperty()
    subject = db.StringProperty()
    type = db.StringProperty() # can be 'groups', 'highpro', 'deep', 'students', 'micro'
    priority = db.IntegerProperty()
    def restore_cache(self):
        logging.info("Restoring Cache of Feed " + self.title)
        #try: 
        updates = self.fetch_entries()
        memcache.set(self.url,updates,86400) # 1 day 
        #except:
            #logging.info("There was a problem downloading " + self.url)
            #pass
    def entries(self):
        if not memcache.get(self.url):
            return [] # TODO: schedule a fetch-task !
        return memcache.get(self.url)
    def fetch_entries(self):
        result = urlfetch.fetch(self.url)
        logging.info("Fetched URL " + self.url)
        updates = []
        if result.status_code == 200:
            feed = feedparser.parse(result.content)
            for entry in feed['entries']:
                x = Entry()
                x.service = self.title
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
    def template_top(self):
        return {'title': self.title, 'entries': self.top_entries() }
      
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
      self.redirect("/bytype")

class TypeView(webapp.RequestHandler):
  def get(self):
    feed_query = Feed.all()
    feed_query.order('priority')

    feeds_template = lambda q: [ feed.template_top() for feed in q ]
    sections_template = lambda n, s: {'name': n, 'feeds': feeds_template( Feed.all().filter("type =", s) ) }
    
    template_values = {
        'types': 
            [ sections_template("Group Blogs", "groups"),
              sections_template("High Profile", "highpro"),
              sections_template("Slow but Deep", "deep"),
              sections_template("Students and Non-Tenure", "students"),
              sections_template("Microblogging", "micro") ]
        }
    
    logging.debug("got here!")
    logging.info("got here 2")
    path = os.path.join(os.path.dirname(__file__), 'bytype.html')
    self.response.out.write(template.render(path, template_values))

class FetchWorker(webapp.RequestHandler):
    def post(self):
        url = self.request.get('url')
        logging.info("FetchWorker: " + url)
        if url:
            feed = Feed.all().filter("url =", url).get()
            if feed:
                feed.restore_cache()
        self.redirect("/")

class FetchAllWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FetchAll")
        for feed in Feed.all():
            logging.info("Adding fetch task for feed " + feed.title)
            taskqueue.add(url="/fetch", params={'url': feed.url})
        self.redirect("/")

class FetchAllSyncWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FetchAllSyn")
        for feed in Feed.all():
            feed.restore_cache()
        self.redirect("/")
        

class InitDatabase(webapp.RequestHandler):
    def get(self):
        if Feed.all().count() == 0:
            feed = Feed()
            feed.url = "http://peter.krautzberger.info/atom.xml"
            feed.title = "thelazyscience"
            feed.person = "Peter Krautzberger"
            feed.subject = "math.LO"
            feed.type = "students"
            feed.priority = 1
            feed.put()
        self.redirect('/')
        

def main():
  application = webapp.WSGIApplication(
                                       [('/', MainPage),
                                        ('/bytype', TypeView),
                                        ('/fetchallsync', FetchAllSyncWorker),
                                        ('/fetchall', FetchAllWorker),
                                        ('/fetch', FetchWorker),
                                        ('/init', InitDatabase)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
