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

import wsgiref.handlers
import os
import xml.dom.minidom
import feedparser
import datetime
import time
import logging
import string
import md5

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

import cgi
from google.appengine.ext.webapp.util import run_wsgi_app

# from http://code.google.com/appengine/docs/python/tools/libraries.html#Django
# import os #done earlier
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96')

#import pickle # for listoflist in datastore
from django.utils import simplejson


### some variables like header, footer etc.
from temp_global import *


# truncating html via http://stackoverflow.com/questions/4970426/html-truncating-in-python
import re
def truncate_html_words(s, num):
    """
    Truncates html to a certain number of words (not counting tags and comments).
    Closes opened tags if they were correctly closed in the given html.
    """
    length = int(num)
    if length <= 0:
        return ''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|([A-Za-z0-9][\w-]*)')
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    ellipsis_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                ellipsis_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or ellipsis_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i+1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:ellipsis_pos] + ' [...]'
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out


## Escape HTML entities.
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
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
### read updated timestamp from entry
def feedparser_entry_to_timestamp_updated(entry):
    t = time.gmtime(0)
    try:
        t = entry.updated_parsed
    except AttributeError:
        pass
    return datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
### creating a reliable guid for our own feeds
def feedparser_entry_to_guid(entry):
    theid = None
    try:
        theid = html_escape(entry.id)
    except AttributeError:
        t = time.gmtime(0)
        try:
            t = entry.updated_parsed
        except AttributeError:
            pass
        dt = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
        try:
            theid = html_escape((entry['link'] + str(dt) + entry.title)[0:500])
        except AttributeError:
            pass
    return theid


###################################################
### The first major class: Feed
###################################################

class Feed(db.Model):
    posts_url = db.LinkProperty()
    homepage = db.StringProperty()
    title = db.StringProperty() # NOTE utf8 -- must be html-escaped in every html context!!!
    listtitle = db.StringProperty()
    person = db.StringProperty()
    category = db.StringProperty() # history fun general commercial art visual pure applied teacher journalism community institution journal news carnival
    taglist = db.StringListProperty()
    language = db.StringProperty()
    priority = db.IntegerProperty()
    favicon = db.StringProperty()
    comments_url = db.StringProperty()
    comments_day = db.IntegerProperty()
    comments_week = db.IntegerProperty()
    posts_week = db.IntegerProperty()
    posts_month = db.IntegerProperty()
    checksum_posts = db.StringProperty() # checksum of original rss-file
    checksum_comments = db.StringProperty() # checksum of original rss-file
    last_successful_posts_fetch_date = db.DateTimeProperty()
    last_successful_comments_fetch_date = db.DateTimeProperty()
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
        logging.info("Feed " + self.title + " has stats " + str(self.comments_day) + " " + str(self.comments_week) + " " + str(self.posts_month) + " " + str(self.posts_week))
        self.put()
    def update_taglist(self):
        self.taglist = [ tag for post in Post.gql("WHERE service = :1", self.title) for tag in post.tags]
        logging.info("Feed " + self.title + " taglist updated ")
        self.put()
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
            m = md5.new(result.content).hexdigest() # creating checksum for successfully fetched feed-content
            if _type == Post: # Deal with the type
                checksum = self.checksum_posts
                last_fetch = self.last_successful_posts_fetch_date
            else:
                checksum = self.checksum_comments
                last_fetch = self.last_successful_comments_fetch_date
            if last_fetch == None:
                last_fetch = datetime.datetime(1970,1,1)
            if checksum != m:
                logging.info("Checksum changed! Processing " + self.title)
                try:
                    feed = feedparser.parse(result.content)
                    for entry in feed['entries']:
                        if (last_fetch - datetime.timedelta(0,600)) <= feedparser_entry_to_timestamp_updated(entry):
                            _type.generate_entry(entry,feed,self) 
                except LookupError, e:
                    logging.warning("There was an error parsing the feed " + url + ":" + str(e))
                if _type == Post: # Deal with the type
                    self.checksum_posts = m
                    self.last_successful_posts_fetch_date = datetime.datetime.now()
                    self.put()
                else:
                    self.checksum_comments = m
                    self.last_successful_comments_fetch_date = datetime.datetime.now()
                    self.put()
                logging.info("Checksum updated: " + self.title)
    #def cse_homepage(self): # REMINDER: for CSE = google custome search engine = search for startpage
     #   return add_slash(strip_http(self.homepage))




###################################################
#### The second major class: Entry
###################################################

class Entry(polymodel.PolyModel):
    title = db.TextProperty()
    link = db.StringProperty()
    homepage = db.StringProperty()
    service = db.StringProperty()
    timestamp_created = db.DateTimeProperty()
    timestamp_updated = db.DateTimeProperty()
    length = db.IntegerProperty()
    content = db.TextProperty() ## TODO change to blob property -- size constraints of textproperty are a problem
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
            guid = feedparser_entry_to_guid(entry)
            timestamp_updated = feedparser_entry_to_timestamp_updated(entry)
            result = cls.gql("WHERE guid = :1", guid).get()
            if result != None and result.timestamp_updated == timestamp_updated:
                return # if nothing has changed we do nothing and return
            x = result # by default we update the entry
            if x == None:
                x = cls() # if the entry does not exist, then we create a new one
                #logging.info("guid does not exist: " + entry['title'])
            #   add entry to database!
            x.service = database_feed.title # NOTE utf8 -- must be html-escaped in every html context!!!
            x.title = html_escape(entry['title']) # feedparser give utf8
            x.link = html_escape(entry['link'])   # feedparser give utf8
            x.length = len( get_feedparser_entry_content(entry) )
##OLD            x.content = get_feedparser_entry_content(entry)
            x.content = truncate_html_words(get_feedparser_entry_content(entry), 100)
            x.category = database_feed.category
            x.homepage = database_feed.homepage
            try:
                x.tags = [ string.capwords(tag.term) for tag in entry.tags ]
            except AttributeError:
                x.tags = [ ]
            x.timestamp_updated = timestamp_updated
            try:
                t = entry.published_parsed
                x.timestamp_created = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
            except AttributeError:
                x.timestamp_created = timestamp_updated
            x.guid = guid
            x.put()
        except Exception, e: # TODO more exception catching: 'NoneType' error when feed is malformed not enough for bug tracking.
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
### TODO Is gettime used anywhere???
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


#######################################
### Storing for caching
#######################################

class Stored_Page(db.Model):
    html_content = db.TextProperty()
    name = db.StringProperty()
    
class JsonProperty(db.TextProperty):
	def validate(self, value):
		return value

	def get_value_for_datastore(self, model_instance):
		result = super(JsonProperty, self).get_value_for_datastore(model_instance)
		result = simplejson.dumps(result)
		return db.Text(result)

	def make_value_from_datastore(self, value):
		try:
			value = simplejson.loads(str(value))
		except:
			pass

		return super(JsonProperty, self).make_value_from_datastore(value)

class Stored_List(db.Model):
   content = JsonProperty()
   name = db.StringProperty()


#######################################
### THE PAGE CONSTRUCTS:  constructs for caching and generating
#######################################



### caching pages in datastore and memcache

class CachedPage(webapp.RequestHandler):
    ### TODO is cachName, cacheTime still relevant?
    cacheName = "default"
    cacheTime = 2700
    mimeType = "application/xhtml+xml"
    def write_page_to_datastore(self):
        x = Stored_Page()
        x.html_content = self.generatePage()
        x.name = self.cacheName
        x.put()
    def get(self):
        if self.cacheName == "": ## the empty string as cacheName turns off caching (e.g. PlanetTAG)
            self.response.out.write(self.generatePage())
        else:
            if not memcache.get(self.cacheName):
                  if not Stored_Page.gql("WHERE name = :1", self.cacheName).get():
                     logging.info("Writing to datastore: " + self.cacheName)
                     self.write_page_to_datastore()
                  content = Stored_Page.gql("WHERE name = :1", self.cacheName).get().html_content
                  if not content == 'NoneType':
                     memcache.set(self.cacheName,content,self.cacheTime) ### TODO NoneType error messages on the App Engine but everything works
                  #except Exception, e:
                   #  logging.warning("Error setting memcache from Stored_Page object :" + str(e))
            self.response.headers['Content-Type'] = self.mimeType
            self.response.out.write(memcache.get(self.cacheName))

### Adding header, footer, menu

class TemplatePage(CachedPage):
    def generatePage(self):
        return header + menu + "<div class='content'>" + self.generateContent() + disqus + "</div>" + footer + "</body></html>"


### TODO remove leftover static cheetah pages???

#class SimpleCheetahPage(CachedPage):
#    templateName = "default.tmpl"
#    def generatePage(self):
#        template_values = { 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
#        path = os.path.join(os.path.dirname(__file__), self.templateName)
#        return str(Template( file = path, searchList = (template_values,) ))

        

#################################
### Generating the static pages 
#################################


#class StartPage(SimpleCheetahPage):
#    cacheName = "StartPage"
#    templateName = "start.tmpl"

#class FeedsPage(SimpleCheetahPage):
#    cacheName = "FeedsPage"
#    templateName = "feeds.tmpl"


#################################
#### CSE = google custom search engine
#################################

### TODO is completely outdated!!!!!

#class CSEConfig(webapp.RequestHandler):
#    def get(self):
#        template_values = { 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
#        path = os.path.join(os.path.dirname(__file__), 'cse-config.tmpl')
#        self.response.out.write(Template( file = path, searchList = (template_values,) ))


#################################
### WORKER CLASSES downloading the feeds
#################################

class FetchWorker(webapp.RequestHandler):
    def post(self):
        try:
            url = self.request.get('url')
            logging.info("FetchWorker: " + url)
            if url:
                feed = Feed.gql("WHERE posts_url = :1", url).get()
                if feed:
                    feed.update_database()
            self.response.set_status(200)
            logging.info("FetchWorker done: " + url)
        except Exception,e:
            self.response.set_status(503)
            logging.warning("FetchWorker failed: " + url + "\n" + str(e))

class AllWorker(webapp.RequestHandler):
    def get(self):
        logging.info("AllWorker")
        for page in Stored_Page.all():
            memcache.delete(page.name)
            page.delete()
        for feed in Feed.all():
            #logging.info("Adding fetch task for feed " + feed.title + " with url: " + feed.posts_url)
            if feed.category != 'community': ### TODO GET YOUR ACT TOGETHER AND RE-ADD THEM 
                taskqueue.add(url="/fetch", params={'url': feed.posts_url})

        pages_to_cache_list = ["/", "/feeds","/bytype","/weekly-picks","/bydate","/byresearchdate","/byartvishisdate","/byteacherdate","/bystats","/planetmo", "/planetmo-feed","/feed_pure","/feed_applied","/feed_history","/feed_art","/feed_fun","/feed_general","/feed_journals","/feed_teachers","/feed_visual","/feed_journalism","/feed_institutions","/feed_communities","/feed_commercial","/feed_newssite","/feed_carnival","/feed_all","/feed_researchers"]
        for page in pages_to_cache_list:
            taskqueue.add(url=page, method="GET")
        self.response.set_status(200)


#################################
### GENERATING TAGLISTS PER FEED AND GLOBAL -- moved out of allworker to enable separate cron jobs
#################################

class FeedTagListFetchWorker(webapp.RequestHandler):
    def post(self):
        try:
            url = self.request.get('url')
            logging.info("FeedTagListFetchWorker: " + url)
            if url:
                feed = Feed.gql("WHERE posts_url = :1", url).get()
                if feed:
                    feed.update_taglist()
            self.response.set_status(200)
            logging.info("TagListFetchWorker done: " + url)
        except Exception,e:
            self.response.set_status(503)
            logging.warning("TagListFetchWorker failed: " + url + "\n" + str(e))

class FeedTagListWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FeedTagListWorker")
        for feed in Feed.gql("WHERE category IN :1", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
            taskqueue.add(url="/feedtaglistfetch", params={'url': feed.posts_url})
        self.response.set_status(200)

class GlobalTagListWorker(webapp.RequestHandler):
    def get(self):
        for stored_list in Stored_List.gql("WHERE name = 'Global_Weighted_Taglist'"):
            stored_list.delete()
            #logging.info("Stored_List deleted: " + stored_list.name)
        x = Stored_List()
        x.name = 'Global_Weighted_Taglist'
        global_taglist = [ tag for feed in Feed.gql("WHERE category IN :1", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']) for tag in feed.taglist]
        global_tagset = set(global_taglist)
        #logging.info("taglist is " + str(global_taglist))
        weighted_taglist = []
        for tag in global_tagset:
            tag_weight = global_taglist.count(tag)
            weighted_taglist.append([tag, tag_weight])
        x.content = weighted_taglist
        x.put()
        self.response.set_status(200)


#################################
### CLEANING UP THE DATASTORE // DELETING OLD ENTRIES
#################################

class CleanUpFeed(webapp.RequestHandler):
    def post(self):
        feed_title = self.request.get("feed_title")
        logging.info("Clean Up Feed " + feed_title)
        for post in Post.gql("WHERE service = :1 AND timestamp_updated < :2 ORDER BY timestamp_updated DESC OFFSET 30", feed_title, datetime.datetime.now() - datetime.timedelta(30)):
            post.delete()
        for comment in Comment.gql("WHERE service = :1 AND timestamp_updated < :2", feed_title, datetime.datetime.now() - datetime.timedelta(7)):
            comment.delete()
        self.response.set_status(200)
        
class CleanUpDatastore(webapp.RequestHandler):
    def get(self):
        for feed in Feed.all():
           taskqueue.add(url="/cleanupfeed",params={"feed_title":feed.title}, queue_name='cleanup-queue')
        self.response.set_status(200)


#################################
### MISCELLANEOUS
#################################

### REBOOT: not really with a purpose right now due to datastore caching.

class RebootCommand(webapp.RequestHandler):
    def get(self):
        logging.info("Reboot")
        memcache.flush_all()
        taskqueue.add(url="/allworker", method="GET")
        self.response.set_status(200)

### CLEARPAGECACHE

class ClearPageCacheCommand(webapp.RequestHandler):
    def get(self):
        logging.info("Clear Page Cache")
        for page in Stored_Page.all():
            memcache.delete(page.name)
            page.delete()
        for stored_list in Stored_List.gql("WHERE name = 'Global_Weighted_Tasklist'"):
            stored_list.delete()
        self.response.set_status(200)


#################################
### Dynamically generated web pages // the main content of the site
#################################

from startpage import *
from dateview import DateView ### TODO make abstract and call with "all, research, teacher, hisartvis"
from dateviewresearch import DateViewResearch
from dateviewteacher import DateViewTeacher
from dateviewhisartvis import DateViewHisArtVis
from categoryview import *
from feedhandler import *
from planettag import *
from planetmo import *
from dataexport import *
from grid import *
from weeklypicks import *
from statsview import * ### TODO make like dateview all, research, teacher, hisartivs
from feedspage import *

  

#################################
### THE M A I N FUNCTION
#################################

def main():
  application = webapp.WSGIApplication(
                                       [('/', StartPage),
                                        ('/clearpagecache', ClearPageCacheCommand),
                                        ('/cleanupdatastore', CleanUpDatastore),
                                        ('/cleanupfeed', CleanUpFeed),
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
                                        ('/cse-config', CSEConfig), ## TODO not up to date at all...
                                        ('/allworker', AllWorker),
                                        ('/fetch', FetchWorker),
                                        ('/feedtaglistfetch', FeedTagListFetchWorker),
                                        ('/feedtaglistworker', FeedTagListWorker),
                                        ('/globaltaglistworker', GlobalTagListWorker),
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
                                        ('/feed_newssite', FeedHandlerNewssite),
                                        ('/feed_carnival', FeedHandlerCarnival),
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

