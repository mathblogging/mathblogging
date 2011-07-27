# Mathblogging is a simple blog aggregator.
# Copyright (C) 2010 Felix Breuer, Frederik von Heymann, Peter Krautzberger
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from Cheetah.Template import Template

import wsgiref.handlers
import os
import xml.dom.minidom
import feedparser
import datetime
import time
import logging
import string

from operator import attrgetter
from time import strftime, strptime, gmtime
from xml.dom.minidom import Node
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue

from temp_global import *

import cgi
from google.appengine.ext.webapp.util import run_wsgi_app

## Escape HTML entities.
#html_escape_table = {
#    "&": "&amp;",
#    '"': "&quot;",
##    "'": "&apos;",
#    ">": "&gt;",
#    "<": "&lt;",
#    }
#
#def html_escape(text):
#    """Produce entities within text."""
#    return "".join(html_escape_table.get(c,c) for c in text)
## end

### strip_http, add_slash: for Google Custom Search
def strip_http(str):
    if str[0:7] == "http://":
      return str[7:]
    else:
      return str

def add_slash(str):
    if str.find("/") == -1:
      return str+"/"
    else:
      return str
### preliminary definitions for processing with feedparser.py
def get_feedparser_entry_content(entry):
    try:
        return " ".join([content.value for content in entry.content])            
    except AttributeError:
        try:
            return entry['summary']
        except AttributeError:
            return ""
### creating a reliable guid for our own feeds
def feedparser_entry_to_guid(entry):
    theid = None
    try:
        theid = entry.id
    except AttributeError:
        t = time.gmtime(0)
        try:
            t = entry.updated_parsed
        except AttributeError:
            pass
        dt = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
        try:
            theid = (entry['link'] + str(dt) + entry.title)[0:500]
        except AttributeError:
            pass
    return theid
### The first major class: Feed
class Feed(db.Model):
    posts_url = db.LinkProperty()
    homepage = db.StringProperty()
    title = db.StringProperty()
    listtitle = db.StringProperty()
    person = db.StringProperty()
    category = db.StringProperty() # history fun general commercial art visual pure applied teacher journalism community institution journal
    language = db.StringProperty()
    priority = db.IntegerProperty()
    favicon = db.StringProperty()
    comments_url = db.StringProperty()
    comments_day = db.IntegerProperty()
    comments_week = db.IntegerProperty()
    posts_week = db.IntegerProperty()
    posts_month = db.IntegerProperty()
    def update_database(self):
        logging.info("Update Database for Feed: " + self.title)
        self.fetch_feed_and_generate_entries(self.posts_url,Post)
        self.fetch_feed_and_generate_entries(self.comments_url,Comment)
        self.update_stats()
    def update_stats(self):
        # calculate stats
        self.comments_day = Comment.gql("WHERE service = :1 AND timestamp_created > :2", self.title, datetime.datetime.now() - datetime.timedelta(1)).count()
        self.comments_week = Comment.gql("WHERE service = :1 AND timestamp_created > :2", self.title, datetime.datetime.now() - datetime.timedelta(7)).count()
        self.posts_week = Post.gql("WHERE service = :1 AND timestamp_created > :2", self.title, datetime.datetime.now() - datetime.timedelta(7)).count()
        self.posts_month = Post.gql("WHERE service = :1 AND timestamp_created > :2", self.title, datetime.datetime.now() - datetime.timedelta(30)).count()
        #self.comments_day = Comment.all().filter("service =",self.title).filter("timestamp_created > ", datetime.datetime.now() - datetime.timedelta(1)).count()
        #self.comments_week = Comment.all().filter("service =",self.title).filter("timestamp_created > ", datetime.datetime.now() - datetime.timedelta(7)).count()
        #self.posts_week = Post.all().filter("service =",self.title).filter("timestamp_created > ", datetime.datetime.now() - datetime.timedelta(7)).count()
        #self.posts_month = Post.all().filter("service =",self.title).filter("timestamp_created > ", datetime.datetime.now() - datetime.timedelta(30)).count()
        logging.info("Feed " + self.title + " has stats " + str(self.comments_day) + " " + str(self.comments_week) + " " + str(self.posts_month) + " " + str(self.posts_week))
        self.put()
    #def entries(self,num=None):
    #    result = [entry for entry in Post.all().filter("service=",self.title)]
    #    return result[0:num]
    def fetch_feed_and_generate_entries(self,url,_type):
        if url == "":
            return
        try:
            result = urlfetch.fetch(url,deadline=10) # 10 is max deadline
        except urlfetch.DownloadError:
            logging.warning("Downloading URL " + url + "failed: timeout.")
            return
        except urlfetch.ResponseTooLargeError:
            logging.warning("Downloading URL " + url + "failed: response tooo large.")
            return
        except urlfetch.InvalidURLError:
            logging.warning("Downloading URL " + url + "failed: invalid url.")
            return
        if result.status_code == 200:
            logging.info("Successfully fetched URL " + url)
            try:
                feed = feedparser.parse(result.content)
                for entry in feed['entries']:
                    _type.generate_entry(entry,feed,self) 
            except LookupError, e:
                logging.warning("There was an error parsing the feed " + url + ":" + str(e))
    def cse_homepage(self): # REMINDER: for CSE = google custome search engine = search for startpage
        return add_slash(strip_http(self.homepage))
    #def top_entries(self):
    #    return self.entries()[0:10]
    #def template_top(self):
    #    return {'title': self.title, 'entries': self.top_entries() }
    # comments_entries the abstract construct
    #def comments_entries(self,num=None):
    #    if not memcache.get(self.comments):
    #        return [] # TODO: schedule a fetch-task !
    #    if num == None:
    #        return memcache.get(self.comments)
    #    result = memcache.get(self.comments)
    #    return result[0:num]

#### The second major class: Entry
class Entry(polymodel.PolyModel):
    title = db.TextProperty()
    link = db.StringProperty()
    homepage = db.StringProperty()
    service = db.StringProperty()
    timestamp_created = db.DateTimeProperty()
    timestamp_updated = db.DateTimeProperty()
    length = db.IntegerProperty()
    content = db.TextProperty()
    tags = db.StringListProperty()
    category = db.StringProperty()
    guid = db.StringProperty()
        
    # cls has to be one of the classes Post or Comment
    # entry is a feedparser entry
    # feedparser_feed is a feedparser feed
    # database_feed is corresponding Feed object
    @classmethod
    def generate_entry(cls, entry, feedparser_feed, database_feed):
        try:
            # if entry is in database, i.e.,
            result = cls.all().filter("service=",database_feed.title).filter("guid=",feedparser_entry_to_guid(entry)).get()
            if result != None:
                #   update entry attributes if changed?
                pass
            else:
                #   add entry to database!
                x = cls()
                x.service = database_feed.title
                x.title = entry['title']
                x.link = entry['link']
                x.length = len( get_feedparser_entry_content(entry) )
                x.content = get_feedparser_entry_content(entry)
                x.category = database_feed.category
                x.homepage = database_feed.homepage
                try:
                    x.tags = [ string.capwords(tag.term) for tag in entry.tags ]
                except AttributeError:
                    x.tags = [ ]
                t = time.gmtime(0)
                try:
                    t = entry.updated_parsed
                except AttributeError:
                    pass
                x.timestamp_updated = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
                try:
                    t = entry.published_parsed
                except AttributeError:
                    pass
                x.timestamp_created = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
                x.guid = feedparser_entry_to_guid(entry)
                x.put()
        except Exception, e:
            logging.warning("There was an error processing an Entry of the Feed :" + str(e))

    def printTime_created_rfc3339(self):
        try:
            res = self.timestamp_created.strftime('%Y-%m-%dT%H:%M:%SZ')
        except TypeError:
            res = ""
        return res

    def printTime_updated_rfc3339(self):
        try:
            res = self.timestamp_updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        except TypeError:
            res = ""
        return res

    def printTime_created(self):
        try:
            res = strftime('%B %d,%Y at %I:%M:%S %p',self.timestamp_created)
        except TypeError:
            res = ""
        return res
    def printTime_updated(self):
        try:
            res = strftime('%B %d,%Y at %I:%M:%S %p',self.timestamp_updated)
        except TypeError:
            res = ""
        return res
### Is gettime used anywhere???
    def gettime(self): #REMINDER for future code reading: change name to gettime_created -- after Felix fixes/improves statsview to fix the bug
        if self.timestamp_created == None:
            return time.gmtime(0)
        else:
            return self.timestamp_created
    def printShortTime_created(self):
        try:
            today = datetime.datetime.now()
            if today.year == self.timestamp_created.year and today.month <= self.timestamp_created.month and today.day <= self.timestamp_created.day:
                return "today"
            res = self.timestamp_created.strftime('%b %d')
        except TypeError, e:
            logging.warning("problem: " + str(e))
            res = ""
        return res

class Post(Entry):
    iamapost = db.StringProperty()

class Comment(Entry):
    iamacomment = db.StringProperty()


### The smaller classes:  preliminary work for generating actual webpages


class MainPage(webapp.RequestHandler):
  def get(self):
      self.redirect("/content/start.html")

class QueryFactory:
  def get(self):
      return Feed.all()

class GqlQueryFactory:
  def get(self, string):
      return db.GqlQuery(string)

class CachedPage(webapp.RequestHandler):
    # NOTE: the empty string as cacheName turns off caching
    cacheName = "default"
    cacheTime = 2700
    def get(self):
        if self.cacheName == "":
            self.response.out.write(self.generatePage())
        else:
            if not memcache.get(self.cacheName):
                memcache.set(self.cacheName,self.generatePage(),self.cacheTime)
            #self.response.headers['Cache-Control'] = 'public; max-age=2700;'
            self.response.out.write(memcache.get(self.cacheName))

class TemplatePage(CachedPage):
    def generatePage(self):
        return header + menu + "<div class='content'>" + self.generateContent() + disqus + "</div>" + footer + "</body></html>"

class SimpleCheetahPage(CachedPage):
    templateName = "default.tmpl"
    def generatePage(self):
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), self.templateName)
        return str(Template( file = path, searchList = (template_values,) ))

### static pages

class StartPage(SimpleCheetahPage):
    cacheName = "StartPage"
    templateName = "start.tmpl"

class AboutPage(SimpleCheetahPage):
    cacheName = "AboutPage"
    templateName = "about.tmpl"

class FeedsPage(SimpleCheetahPage):
    cacheName = "FeedsPage"
    templateName = "feeds.tmpl"

### the old Dynamic pages -- OBSOLETE?

#class CategoryView(SimpleCheetahPage):
#    cacheName = "CategoryView"
#    templateName = "bycategory.tmpl"

class WeeklyPicks(SimpleCheetahPage):
    cacheName = "WeeklyPicks"
    # TODO: do everything in template???
    def generatePage(self):
        # ############ PROBLEM SOLVED ############
        # This is how to test list membership (even though it is counter-intuitive), see:
        #  http://wenku.baidu.com/view/7861b3f9aef8941ea76e0562.html
        #  http://code.google.com/p/typhoonae/issues/detail?id=40
        # 
        picks = Post.gql("WHERE service = 'Mathblogging.org - the Blog' AND tags = 'weekly picks' ORDER BY timestamp_created LIMIT 15")
        template_values = { 'qf': QueryFactory(), 'picks_entries': picks, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
        
        path = os.path.join(os.path.dirname(__file__), 'weekly_picks.tmpl')
        return str(Template( file = path, searchList = (template_values,) ))
        
        
class StatsView(CachedPage):
    cacheName = "StatsView"
    # TODO: do everything in template???
    def generatePage(self):
        feeds_w_comments_day = db.GqlQuery("SELECT * FROM Feed WHERE comments_day != 0 ORDER BY comments_day DESC").fetch(1000)
        feeds_w_comments_week = db.GqlQuery("SELECT * FROM Feed WHERE comments_week != 0 ORDER BY comments_week DESC").fetch(1000)
        feeds_w_posts_week = db.GqlQuery("SELECT * FROM Feed WHERE posts_week != 0 ORDER BY posts_week DESC").fetch(1000)
        feeds_w_posts_month = db.GqlQuery("SELECT * FROM Feed WHERE posts_month != 0 ORDER BY posts_month DESC").fetch(1000)
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'comments_week': feeds_w_comments_week, 'comments_day': feeds_w_comments_day, 'posts_week': feeds_w_posts_week, 'posts_month': feeds_w_posts_month, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
            
        path = os.path.join(os.path.dirname(__file__), 'bystats.tmpl')
        renderedString = str(Template( file = path, searchList = (template_values,) ))
        return renderedString

        
class DateResearchView(CachedPage):
    cacheName = "DateResearchView"
    # TODO: do everything in template???
    def get(self):
        template_values = { 'qf':  QueryFactory(), 
                            'allentries': Post.gql("WHERE category IN ['pure','applied'] ORDER BY timestamp_created LIMIT 150"), 
                            'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'bydate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class DateHisArtVisView(CachedPage):
    cacheName = "DateHisArtVisView"
    def get(self):
        template_values = { 'qf':  QueryFactory(), 
                            'allentries': Post.gql("WHERE category IN ['visual','history','art'] ORDER BY timestamp_created LIMIT 150"),
                            'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'bydate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class DateTeacherView(CachedPage):
    cacheName = "DateTeacherView"
    def get(self):
        template_values = { 'qf':  QueryFactory(), 
                            'allentries': Post.gql("WHERE category = 'teacher' ORDER BY timestamp_created LIMIT 150"),
                            'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'bydate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class PlanetMO(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 
                            'moentries': Post.gql("WHERE tags IN ['mathoverflow','mo','planetmo'] ORDER BY timestamp_created LIMIT 50"), 
                            'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
    
        path = os.path.join(os.path.dirname(__file__), 'planetmo.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

# Database output
class CsvView(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
    
        path = os.path.join(os.path.dirname(__file__), 'database.tmpl')
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

## Database OPML output
#class OPMLView(webapp.RequestHandler):
#    def get(self):
#        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
#    
#        path = os.path.join(os.path.dirname(__file__), 'opml.tmpl')
#        self.response.headers['Content-Type'] = 'text/xml'
#        self.response.out.write(Template( file = path, searchList = (template_values,) ))

#### CSE = google custom search engine
class CSEConfig(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'cse-config.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


### Worker classes: downloading the feeds
class FetchWorker(webapp.RequestHandler):
    def post(self):
        try:
            url = self.request.get('url')
            logging.info("FetchWorker: " + url)
            if url:
                feed = Feed.all().filter("posts_url =", url).get()
                if feed:
                    feed.update_database()
            self.response.set_status(200)
            logging.info("FetchWorker done: " + url)
        except Exception,e:
            self.response.set_status(200)
            logging.warning("FetchWorker failed: " + url + "\n" + str(e))

class AllWorker(webapp.RequestHandler):
    def get(self):
        logging.info("AllWorker")
        for feed in Feed.all():
            #logging.info("Adding fetch task for feed " + feed.title + " with url: " + feed.posts_url)
            taskqueue.add(url="/fetch", params={'url': feed.posts_url})
        taskqueue.add(url="/taglistworker", method="GET")
        self.response.set_status(200)
 
class RebootCommand(webapp.RequestHandler):
    def get(self):
        logging.info("Reboot")
        memcache.flush_all()
        taskqueue.add(url="/allworker")
        self.response.set_status(200)

### Dynamically generated web pages -- the main content of the site

from dateview import DateView
from dateviewresearch import DateViewResearch
from dateviewteacher import DateViewTeacher
from dateviewhisartvis import DateViewHisArtVis
from categoryview import CategoryView
from feedhandler import *
from planettag import *
from planetmo import *
from dataexport import *
from grid import *
from weeklypicks import *

### the main function.

def main():
  application = webapp.WSGIApplication(
                                       [('/', StartPage),
                                        ('/about', AboutPage),
                                        ('/feeds', FeedsPage),
                                        ('/bytype', CategoryView),
                                        ('/weekly-picks', WeeklyPicks),
                                        ('/bydate', DateView),
                                        ('/byresearchdate', DateViewResearch),
                                        ('/byartvishisdate', DateViewHisArtVis),
                                        ('/byteacherdate', DateViewTeacher),
                                        ('/bystats', StatsView),
                                        ('/planetmo', PlanetMO),
                                        ('/planetmo-feed', PlanetMOfeed),
                                        ('/database.csv', CsvView),
                                        ('/database-opml.xml', OPMLView),
                                        ('/cse-config', CSEConfig),
                                        ('/allworker', AllWorker),
                                        ('/fetch', FetchWorker),
                                        ('/taglistworker', TagListWorker),
                                        ('/reboot', RebootCommand),
                                        ('/feed_pure', FeedHandlerPure),
                                        ('/feed_applied', FeedHandlerApplied),
                                        ('/feed_history', FeedHandlerHistory),
                                        ('/feed_art', FeedHandlerArt),
                                        ('/feed_fun', FeedHandlerFun),
                                        ('/feed_general', FeedHandlerGeneral),
                                        ('/feed_journals', FeedHandlerJournals),
                                        ('/feed_teachers', FeedHandlerTeachers),
                                        ('/feed_visual', FeedHandlerVisual),
                                        ('/feed_journalism', FeedHandlerJournalism),
                                        ('/feed_institutions', FeedHandlerInstitutions),
                                        ('/feed_communities', FeedHandlerCommunities),
                                        ('/feed_commercial', FeedHandlerCommercial),
                                        ('/feed_all', FeedHandlerAll),
                                        ('/feed_researchers', FeedHandlerResearchers),
                                        ('/feed_people', FeedHandlerPeople),
                                        ('/feed_large', FeedHandlerAll), # left for transition
                                        ('/feed_groups', FeedHandlerResearchers),# left for transition
                                        ('/feed_educator', FeedHandlerTeachers), # left for transition
                                        ('/feed_small', FeedHandlerPeople), # left for transistion
                                        ('/feed_academics', FeedHandlerResearchers), # left for transition
                                        ('/feed_institution', FeedHandlerInstitutions),
                                        ('/planettag', PlanetTag),
                                        # Testing
                                        ('/gridview', GridView)
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()

