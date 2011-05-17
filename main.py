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
import counter

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

import cgi
from google.appengine.ext.webapp.util import run_wsgi_app

# Escape HTML entities.
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
#    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
# end

header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8"/>
    <link rel="stylesheet" type="text/css" href="/content/site.css"/>
    <link rel="icon" href="/favicon.ico" type="image/x-icon" />
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />
    <title>Mathblogging.org</title>
    <script type="text/javascript" src="/content/jquery-1.5.2.min.js"></script>         
    <link rel="stylesheet" type="text/css" href="/content/jqcloud.css" />
    <script type="text/javascript" src="/content/jqcloud-0.1.8.js"></script>
  </head>
  <body>
    <h1> <a style="text-decoration:none;color:white;" href="/">Mathblogging.org <small style="color: #CCC">beta</small></a></h1>
"""

menu = """
<!-- Top Navigation -->
<div id="menu">
<ul>
  <li><h2><a href="/bydate" title="Recent posts">Posts</a></h2>
  <ul>
    <li><h2><a href="/byresearchdate" title="Recent posts in Research">Researchers</a></h2>
    </li>
    <li><h2><a href="/bygroupdate" title="Recent posts in Groups">Groups</a></h2>
    </li>
    <li><h2><a href="/byeducatordate" title="Recent posts from Educators">Educators</a></h2>
    </li>
  </ul>
  </li>
  <li><h2><a href="/bytype" title="Blogs by Category">Blogs</a></h2>
  </li>
  <li><h2><a href="/bystats" title="Recent statistics">Stats</a></h2>
  </li>
  <li><h2><a href="/weekly-picks" title="Our weekly picks">Weekly Picks</a></h2>
  </li>     
  <li><h2><a href="/planetmo" title="PlanetMO">PlanetMO</a></h2>
  </li>     
  <li><h2><a href="/feeds" title="Feeds">Feeds</a></h2>
  </li>
  <li><h2><a href="https://mathblogging.wordpress.com/" title="Developer Blog">Blog</a></h2>
  </li>
  <li><h2><a href="/" title="Search">Search</a></h2>
  </li>
</ul>						
</div>
<!-- end Top Navigation -->
"""

disqus = """
<!-- disqus code-->
<div class="disqus">
<hr/>
<div id="disqus_thread"></div>
<script type="text/javascript">
    /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
    var disqus_shortname = 'mathblogging'; // required: replace example with your forum shortname

    // The following are highly recommended additional parameters. Remove the slashes in front to use.
    // var disqus_identifier = 'unique_dynamic_id_1234';
    // var disqus_url = 'http://example.com/permalink-to-page.html';

    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
<noscript><p>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></p></noscript>
<a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
</div>
<!-- end disqus code-->
"""

footer = """
<!-- copyright footer -->
<div class="footer">
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">
  <img alt="Creative Commons License" src="http://i.creativecommons.org/l/by-nc-sa/3.0/80x15.png"/>
</a>
<p>
mathblogging.org is licensed under a <br/> <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License</a>.
</p>
</div>
<!-- end copyright footer -->
"""

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

def get_feedparser_entry_content(entry):
    try:
        return " ".join([content.value for content in entry.content])            
    except AttributeError:
        try:
            return entry['summary']
        except AttributeError:
            return ""
            

class Feed(db.Model):
    url = db.LinkProperty()
    homepage = db.StringProperty()
    title = db.StringProperty()
    listtitle = db.StringProperty()
    person = db.StringProperty()
    subject = db.StringListProperty()
    type = db.StringProperty() # can be 'groups', 'research', 'educator', 'journalism', 'institution', 'community', ('commercial')
    priority = db.IntegerProperty()
    favicon = db.StringProperty()
    comments = db.StringProperty()
    def restore_cache(self):
        logging.info("Restoring Cache of Feed " + self.title)
        #try: 
        updates = self.fetch_entries()
        memcache.set(self.url,updates,86400) # 1 day 
        # memcache element for comment feeds. fetch_comments_entries accumulates the list, self.comments is the database object to call up later
        comments_updates = self.fetch_comments_entries()
        memcache.set(self.comments,comments_updates,86400) # 1 day 
        #except:
            #logging.info("There was a problem downloading " + self.url)
            #pass
    def entries(self,num=None):
        if not memcache.get(self.url):
            return [] # TODO: schedule a fetch-task !
        if num == None:
            return memcache.get(self.url)
        result = memcache.get(self.url)
        return result[0:num]
    def fetch_entries(self):
        try:
            result = urlfetch.fetch(self.url,deadline=10) # 10 is max deadline
        except urlfetch.DownloadError:
            logging.warning("Downloading URL " + self.url + "failed: timeout.")
            return []
        except urlfetch.ResponseTooLargeError:
            logging.warning("Downloading URL " + self.url + "failed: response tooo large.")
            return []
        updates = []
        if result.status_code == 200:
            logging.info("Successfully fetched URL " + self.url)
            try:
                feed = feedparser.parse(result.content)
                for entry in feed['entries']:
                    try:
                        x = Entry()
                        x.service = self.title
                        x.title = entry['title']
                        x.link = html_escape(entry['link'])
                        x.length = len( get_feedparser_entry_content(entry) )
                        x.content = get_feedparser_entry_content(entry)
                        #x.cleancontent = ' '.join(BeautifulSoup(x.content).findAll(text=True))
                        #x.sanitizedcontent = x.content
                        x.homepage = self.homepage
                        try:
                            x.tags = entry.tags
                        except AttributeError:
                            x.tags = [ ]
                        try:
                            x.timestamp_updated = entry.updated_parsed
                        except AttributeError:
                            #x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
                            x.timestamp_updated = time.gmtime(0)
                        try:
                            x.timestamp_created = entry.published_parsed
                        except AttributeError:
                            try:
                                x.timestamp_created = entry.updated_parsed
                            except AttributeError:
                                #x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
                                x.timestamp_created = time.gmtime(0)
                        updates.append(x)
                    except Exception, e:
                        logging.warning("There was an error processing an Entry of the Feed " + self.title + ":" + str(e))        
            except LookupError, e:
                logging.warning("There was an error parsing the feed " + self.title + ":" + str(e))
                    
        return updates
    def cse_homepage(self):
        return add_slash(strip_http(self.homepage))
    def top_entries(self):
        return self.entries()[0:10]
    def template_top(self):
        return {'title': self.title, 'entries': self.top_entries() }
    # comments_entries the abstract construct
    def comments_entries(self,num=None):
        if not memcache.get(self.comments):
            return [] # TODO: schedule a fetch-task !
        if num == None:
            return memcache.get(self.comments)
        result = memcache.get(self.comments)
        return result[0:num]
    # fetching entries from comment feeds (just like regular feed)
    def fetch_comments_entries(self):
        if self.comments == "":
            return []
        try:
            result = urlfetch.fetch(self.comments,deadline=10) # 10 is max deadline
        except urlfetch.DownloadError:
            logging.warning("Downloading URL " + self.comments + "failed: timeout.")
            return []
        except urlfetch.ResponseTooLargeError:
            logging.warning("Downloading URL " + self.comments + "failed: response tooo large.")
            return []
        except urlfetch.InvalidURLError:
            logging.warning("Downloading URL " + self.comments + "failed: invalid url.")
            return []
        comments_updates = []
        if result.status_code == 200:
            logging.info("Successfully fetched URL " + self.comments)
            try:
                feed = feedparser.parse(result.content)
                for entry in feed['entries']:
                    try:
                        x = Entry()
                        x.service = html_escape(self.title)
                        x.title = html_escape(entry['title'])
                        x.link = html_escape(entry['link'])
                        x.length = len( get_feedparser_entry_content(entry) )
                        x.homepage = self.homepage
                        try:
                            x.timestamp_updated = entry.updated_parsed
                        except AttributeError:
                            #x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
                            x.timestamp_updated = time.gmtime(0)
                        try:
                            x.timestamp_created = entry.published_parsed
                        except AttributeError:
                            #x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
                            x.timestamp_created = time.gmtime(0)
                        comments_updates.append(x)
                    except Exception, e:
                        logging.warning("There was an error processing an Entry of the Feed " + self.title + ":" + str(e))        
            except LookupError, e:
                logging.warning("There was an error parsing the feed " + self.title + ":" + str(e))
                    
        return comments_updates
      
    #Function to calculate the number of comments last 24h   (conversion into seconds)
    def comments_day(self):
        return len([item for item in self.comments_entries() if time.mktime(time.localtime()) - time.mktime(item.gettime()) <= 86400 ])
    #Function to calculate the number of comments last 7 days (conversion into seconds)
    def comments_week(self):
        return len([item for item in self.comments_entries() if time.mktime(time.localtime()) - time.mktime(item.gettime()) <= 604800 ])
    #Function to calculate the number of posts last 30 days (conversion into seconds)
    def posts_month(self):
        return len([item for item in self.entries() if time.mktime(time.localtime()) - time.mktime(item.gettime()) <= 2592000 ])
    #Function to calculate the number of posts last 7 days (conversion into seconds)
    def posts_week(self):
        return len([item for item in self.entries() if time.mktime(time.localtime()) - time.mktime(item.gettime()) <= 604800 ])

class Entry:
    def __init__(self=None, title=None, link=None, timestamp_created=None, timestamp_updated=None, service=None, homepage=None, length=0, content="", cleancontent="", sanitizedcontent=""):
        self.title = title
        self.link = link
        self.homepage = homepage
        self.service = service
        self.timestamp_created = timestamp_created
        self.timestamp_updated = timestamp_updated
        self.length = length
        self.content = content
        self.cleancontent = cleancontent
        self.sanitizedcontent = sanitizedcontent
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
    def gettime(self): #REMINDER for future code reading: change name to gettime_created -- after Felix fixes/improves statsview to fix the bug
        if self.timestamp_created == None:
            return time.gmtime(0)
        else:
            return self.timestamp_created
    def printShortTime_created(self):
        try:
            today = time.localtime()
            if today[0] == self.timestamp_created[0] and today[1] <= self.timestamp_created[1] and today[2] <= self.timestamp_created[2]:
                return "today"
            #if today[0] == self.timestamp[0] and today[1] <= self.timestamp[1] and today[2] - 1 <= self.timestamp[2]:
            #    return "yesterday"
            res = strftime('%b %d',self.timestamp_created)
        except TypeError:
            res = ""
        return res

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
    cacheName = "default"
    cacheTime = 2700
    def get(self):
        if not memcache.get(self.cacheName):
            memcache.set(self.cacheName,self.generatePage(),self.cacheTime)
        #self.response.headers['Cache-Control'] = 'public; max-age=2700;'
        self.response.out.write(memcache.get(self.cacheName))

class SimpleCheetahPage(CachedPage):
    templateName = "default.tmpl"
    def generatePage(self):
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), self.templateName)
        return str(Template( file = path, searchList = (template_values,) ))

class StartPage(SimpleCheetahPage):
    cacheName = "StartPage"
    templateName = "start.tmpl"

class AboutPage(SimpleCheetahPage):
    cacheName = "AboutPage"
    templateName = "about.tmpl"

class FeedsPage(SimpleCheetahPage):
    cacheName = "FeedsPage"
    templateName = "feeds.tmpl"

class TypeView(SimpleCheetahPage):
    cacheName = "TypeView"
    templateName = "bytype.tmpl"

class WeeklyPicks(SimpleCheetahPage):
       cacheName = "WeeklyPicks"
       def generatePage(self):
        entries = [ entry for feed in Feed.all().filter("person =","mathblogging.org") for entry in feed.entries() ]
        has_tag = lambda entry: len(filter(lambda tag: tag.term.lower() == "weekly picks", entry.tags)) > 0
        picks = filter(has_tag, entries)
        picks.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf': QueryFactory(), 'picks_entries': picks, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
        
        path = os.path.join(os.path.dirname(__file__), 'weekly_picks.tmpl')
        return str(Template( file = path, searchList = (template_values,) ))
        
        
class RankingView(CachedPage):
    cacheName = "RankingView"
    def generatePage(self):
        feeds_w_comments_day = [ [feed,feed.comments_day()] for feed in Feed.all() if feed.comments_day() != 0]
        feeds_w_comments_week = [ [feed,feed.comments_week()] for feed in Feed.all() if feed.comments_week() != 0]
        feeds_w_comments_day.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_comments_week.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_posts_week = [ [feed,feed.posts_week()] for feed in Feed.all().filter("type !=","community") if feed.posts_week() != 0]
        feeds_w_posts_month = [ [feed,feed.posts_month()] for feed in Feed.all().filter("type !=","community") if feed.posts_month() != 0]
        feeds_w_posts_week.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_posts_month.sort( lambda x,y: - cmp(x[1],y[1]) )
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'comments_week': feeds_w_comments_week, 'comments_day': feeds_w_comments_day, 'posts_week': feeds_w_posts_week, 'posts_month': feeds_w_posts_month, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
            
        path = os.path.join(os.path.dirname(__file__), 'byranking.tmpl')
        renderedString = str(Template( file = path, searchList = (template_values,) ))
        return renderedString

class DateView(CachedPage):
    cacheName = "DateView"
    def generatePage(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","institution").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), 'bydate.tmpl')
        return str(Template( file = path, searchList = (template_values,) ))

        
class DateResearchView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type =","research") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'byresearchdate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class DateGroupView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type =","groups") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'bygroupdate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class DateEducatorView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type =","group") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }

        path = os.path.join(os.path.dirname(__file__), 'byeducatordate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class TagsView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'bytags.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class PlanetMath(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all() for entry in feed.entries() ]
        has_tag_math = lambda entry: len(filter(lambda tag: tag.term.lower().find("math") == 0, entry.tags)) > 0
        entries_tagged_math = filter(has_tag_math, all_entries)
        entries_tagged_math.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'mathentries': entries_tagged_math[0:20], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'planetmath.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class PlanetMO(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all() for entry in feed.entries() ]
        has_tag_math = lambda entry: len(filter(lambda tag: tag.term.lower() == "mathoverflow" or tag.term.lower() == "mo" or tag.term.lower() == "planetmo", entry.tags)) > 0
        entries_tagged_math = filter(has_tag_math, all_entries)
        entries_tagged_math.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'moentries': entries_tagged_math[0:50], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
    
        path = os.path.join(os.path.dirname(__file__), 'planetmo.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class PlanetMOfeed(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all() for entry in feed.entries() ]
        has_tag_math = lambda entry: len(filter(lambda tag: tag.term.lower() == "mathoverflow" or tag.term.lower() == "mo" or tag.term.lower() == "planetmo", entry.tags)) > 0
        entries_tagged_math = filter(has_tag_math, all_entries)
        entries_tagged_math.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': entries_tagged_math, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'atom.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


class CsvView(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
    
        path = os.path.join(os.path.dirname(__file__), 'database.tmpl')
        self.response.headers['Content-Type'] = 'text/csv'
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


class SearchView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'search.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class CSEConfig(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'cse-config.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


class FeedHandlerBase(CachedPage):
    def generatePage(self):
        all_entries = [ entry for feed in self.feeds() for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'atom.tmpl')
        return str(Template( file = path, searchList = (template_values,) ))
        
class FeedHandlerAll(FeedHandlerBase):
    cacheName = "FeedAll"
    def feeds(self):
        return Feed.all()

class FeedHandlerResearcher(FeedHandlerBase):
    cacheName = "FeedResearcher"
    def feeds(self):
        return Feed.all().filter("type =","research")

class FeedHandlerGroups(FeedHandlerBase):
    cacheName = "FeedGroups"
    def feeds(self):
        return Feed.all().filter("type =","groups")

class FeedHandlerEducator(FeedHandlerBase):
    cacheName = "FeedEducator"
    def feeds(self):
        return Feed.all().filter("type =","educator")

class FeedHandlerJournalism(FeedHandlerBase):
    cacheName = "FeedJournalism"
    def feeds(self):
        return Feed.all().filter("type =","journalism")
    
class FeedHandlerInstitutions(FeedHandlerBase):
    cacheName = "FeedInstitutions"
    def feeds(self):
        return Feed.all().filter("type =","institution")

class FeedHandlerCommunities(FeedHandlerBase):
    cacheName = "FeedCommunities"
    def feeds(self):
        return Feed.all().filter("type =","community")

class FeedHandlerPeople(FeedHandlerBase):
    cacheName = "FeedPeople"
    def feeds(self):
        return Feed.all().filter("type !=","community").filter("type !=","institution")

class FeedHandlerAcademics(FeedHandlerBase):
    cacheName = "FeedAcademics"
    def feeds(self):
        return Feed.all().filter("type !=","community").filter("type !=","educator").filter("type !=","journalism")       
    
    

class FetchWorker(webapp.RequestHandler):
    def post(self):
        try:
            url = self.request.get('url')
            logging.info("FetchWorker: " + url)
            if url:
                feed = Feed.all().filter("url =", url).get()
                if feed:
                    feed.restore_cache()
            self.response.set_status(200)
            logging.info("FetchWorker done: " + url)
        except Exception:
            self.response.set_status(200)
            logging.warning("FetchWorker failed: " + url)

class FetchAllWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FetchAll")
        for feed in Feed.all():
            logging.info("Adding fetch task for feed " + feed.title)
            taskqueue.add(url="/fetch", params={'url': feed.url})
        self.response.set_status(200)
 
class FetchAllSyncWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FetchAllSyn")
        for feed in Feed.all():
            feed.restore_cache()
        self.response.set_status(200)

class RebootCommand(webapp.RequestHandler):
    def get(self):
        logging.info("Reboot")
        memcache.flush_all()
        taskqueue.add(url="/fetchall")
        self.response.set_status(200)

class ClearPageCacheCommand(webapp.RequestHandler):
    def get(self):
        logging.info("Clear Page Cache")
        memcache.delete_multi(["StartPage","AboutPage","FeedsPage","TypeView","WeeklyPicks","DateView","RankingView"])
        self.response.set_status(200)
        
class InitDatabase(webapp.RequestHandler):
    def get(self):
        if Feed.all().count() == 0:
            feed = Feed()
            feed.url = "http://peter.krautzberger.info/atom.xml"
            feed.homepage = "http://peter.krautzberger.info"
            feed.title = "thelazyscience"
            feed.person = "Peter Krautzberger"
            feed.subject = ["math.LO"]
            feed.type = "students"
            feed.priority = 1
            feed.favicon = "http://www.mathblogging.org/content/favicon.ico"
            feed.comments = "http://thelazyscience.disqus.com/latest.rss"
            feed.put()
        self.redirect('/')
        
class PlanetTag(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all() for entry in feed.entries() ]
        tagname = self.request.get('content')
        has_tag = lambda entry: len(filter(lambda tag: tag.term.lower() == tagname, entry.tags)) > 0
        entries_tagged = filter(has_tag, all_entries)
        entries_tagged.sort( lambda a,b: - cmp(a.timestamp_created,b.timestamp_created) )
        all_tag = [ tag.term for entry in all_entries for tag in entry.tags ]
        all_tags = list(set(all_tag))
        common_tags = counter.Counter(all_tag).most_common(100)
        template_values = { 'qf':  QueryFactory(), 'moentries': entries_tagged[0:50], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header, 'tagname': tagname, 'alltags': all_tags, 'commontags': common_tags}
    
        path = os.path.join(os.path.dirname(__file__), 'planettag.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


def main():
  application = webapp.WSGIApplication(
                                       [('/', StartPage),
                                        ('/about', AboutPage),
                                        ('/feeds', FeedsPage),
                                        ('/bytype', TypeView),
                                        ('/weekly-picks', WeeklyPicks),
                                        ('/bydate', DateView),
                                        ('/byresearchdate', DateResearchView),
                                        ('/bygroupdate', DateGroupView),
                                        ('/byeducatordate', DateEducatorView),
                                        ('/bytags', TagsView),
                                        ('/bystats', RankingView),
                                        ('/planetmath', PlanetMath),
                                        ('/planetmo', PlanetMO),
                                        ('/planetmo-feed', PlanetMOfeed),
                                        ('/database.csv', CsvView),
                                        ('/search', SearchView),
                                        ('/cse-config', CSEConfig),
                                        ('/fetchallsync', FetchAllSyncWorker),
                                        ('/fetchall', FetchAllWorker),
                                        ('/fetch', FetchWorker),
                                        ('/reboot', RebootCommand),
                                        ('/clearpagecache', ClearPageCacheCommand),
                                        ('/init', InitDatabase),
                                        ('/feed_all', FeedHandlerAll),
                                        ('/feed_large', FeedHandlerAll),
                                        ('/feed_researcher', FeedHandlerResearcher),
                                        ('/feed_groups', FeedHandlerGroups),
                                        ('/feed_educator', FeedHandlerEducator),
                                        ('/feed_journalism', FeedHandlerJournalism),
                                        ('/feed_institution', FeedHandlerInstitutions),
                                        ('/feed_people', FeedHandlerPeople),
                                        ('/feed_small', FeedHandlerPeople),
                                        ('/feed_academics', FeedHandlerAcademics),
                                        ('/feed_communities', FeedHandlerCommunities),
                                        ('/planettag', PlanetTag)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
