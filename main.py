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
  </head>
  <body>
    <h1> <a style="text-decoration:none;color:white;" href="/">Mathblogging.org <small style="color: #CCC">beta</small></a></h1>
"""

menu = """
<!-- Top Navigation -->
<div id="menu">
<ul>
  <li><h2><a href="/bydate" title="Latest Posts">Latest Posts</a></h2>
  </li>
  <li><h2><a href="/bytype" title="Blogs by Category">Blogs by Category</a></h2>
  </li>
  <li><h2><a href="/bychoice" title="Our Favorites">Our Favorites</a></h2>
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
        return ""

class Feed(db.Model):
    url = db.LinkProperty()
    homepage = db.StringProperty()
    title = db.StringProperty()
    person = db.StringProperty()
    subject = db.StringListProperty()
    type = db.StringProperty() # can be 'groups', 'research', 'educator', 'micro', 'mathblogging'
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
                        x.service = html_escape(self.title)
                        x.title = html_escape(entry['title'])
                        x.link = html_escape(entry['link'])
                        x.length = len( get_feedparser_entry_content(entry) )
                        x.homepage = self.homepage
                        try:
                            x.timestamp = entry.updated_parsed
                        except AttributeError:
                            x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
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
        try:
            result = urlfetch.fetch(self.comments,deadline=10) # 10 is max deadline
        except urlfetch.DownloadError:
            logging.warning("Downloading URL " + self.comments + "failed: timeout.")
            return []
        except urlfetch.ResponseTooLargeError:
            logging.warning("Downloading URL " + self.comments + "failed: response tooo large.")
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
                            x.timestamp = entry.updated_parsed
                        except AttributeError:
                            #x.timestamp = time.strptime("01.01.1970","%d.%m.%Y")
                            x.timestamp = time.gmtime(0)
                        comments_updates.append(x)
                    except Exception, e:
                        logging.warning("There was an error processing an Entry of the Feed " + self.title + ":" + str(e))        
            except LookupError, e:
                logging.warning("There was an error parsing the feed " + self.title + ":" + str(e))
                    
        return comments_updates
      
    #Function to calculate the number of comments last 24h   (conversion into seconds)
    def comments_day(self):
        return len([item for item in self.comments_entries() if time.mktime(time.localtime()) - time.mktime(item.timestamp) <= 86400 ])
    #Function to calculate the number of comments last 7 days (conversion into seconds)
    def comments_week(self):
        return len([item for item in self.comments_entries() if time.mktime(time.localtime()) - time.mktime(item.timestamp) <= 604800 ])
    #Function to calculate the number of posts last 30 days (conversion into seconds)
    def posts_month(self):
        return len([item for item in self.entries() if time.mktime(time.localtime()) - time.mktime(item.timestamp) <= 2592000 ])
    #Function to calculate the number of posts last 7 days (conversion into seconds)
    def posts_week(self):
        return len([item for item in self.entries() if time.mktime(time.localtime()) - time.mktime(item.timestamp) <= 604800 ])

class Entry:
    def __init__(self=None, title=None, link=None, timestamp=None, content=None, service=None, homepage=None, length=0):
        self.title = title
        self.link = link
        self.homepage = homepage
        self.service = service
        self.timestamp = timestamp
        self.length = length
    def printTime(self):
        try:
            res = strftime('%B %d,%Y at %I:%M:%S %p',self.timestamp)
        except TypeError:
            res = ""
        return res
    def printShortTime(self):
        try:
            today = time.localtime()
            if today[0] == self.timestamp[0] and today[1] <= self.timestamp[1] and today[2] <= self.timestamp[2]:
                return "today"
            #if today[0] == self.timestamp[0] and today[1] <= self.timestamp[1] and today[2] - 1 <= self.timestamp[2]:
            #    return "yesterday"
            res = strftime('%b %d',self.timestamp)
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

class StartPage(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), 'start.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class AboutPage(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), 'about.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class FeedsPage(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
        path = os.path.join(os.path.dirname(__file__), 'feeds.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class TypeView(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'bytype.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))
        
class ChoiceView(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'bychoice.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

# testing
class RankingView(webapp.RequestHandler):
    def get(self):
        feeds_w_comments_day = [ [feed,feed.comments_day()] for feed in Feed.all() if feed.comments_day() != 0]
        feeds_w_comments_week = [ [feed,feed.comments_week()] for feed in Feed.all() if feed.comments_week() != 0]
        feeds_w_comments_day.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_comments_week.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_posts_week = [ [feed,feed.posts_week()] for feed in Feed.all() if feed.posts_week() != 0]
        feeds_w_posts_month = [ [feed,feed.posts_month()] for feed in Feed.all() if feed.posts_month() != 0]
        feeds_w_posts_week.sort( lambda x,y: - cmp(x[1],y[1]) )
        feeds_w_posts_month.sort( lambda x,y: - cmp(x[1],y[1]) )
        template_values = { 'qf':  QueryFactory(), 'gqf': GqlQueryFactory(), 'comments_week': feeds_w_comments_week, 'comments_day': feeds_w_comments_day, 'posts_week': feeds_w_posts_week, 'posts_month': feeds_w_posts_month, 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'byranking.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class DateView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp,b.timestamp) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'bydate.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))
        
class CsvView(webapp.RequestHandler):
    def get(self):
        template_values = { 'qf':  QueryFactory(), 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header}
    
        path = os.path.join(os.path.dirname(__file__), 'database.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))


class SearchView(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp,b.timestamp) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'search.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class CSEConfig(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp,b.timestamp) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'footer': footer, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'cse-config.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class FeedHandler1(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all().filter("type !=","micro").filter("type !=","community") for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp,b.timestamp) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'atom.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))

class FeedHandler2(webapp.RequestHandler):
    def get(self):
        all_entries = [ entry for feed in Feed.all() for entry in feed.entries() ]
        all_entries.sort( lambda a,b: - cmp(a.timestamp,b.timestamp) )
        template_values = { 'qf':  QueryFactory(), 'allentries': all_entries[0:150], 'menu': menu, 'disqus': disqus, 'header': header }
    
        path = os.path.join(os.path.dirname(__file__), 'atom.tmpl')
        self.response.out.write(Template( file = path, searchList = (template_values,) ))
    

class FetchWorker(webapp.RequestHandler):
    def post(self):
        url = self.request.get('url')
        logging.info("FetchWorker: " + url)
        if url:
            feed = Feed.all().filter("url =", url).get()
            if feed:
                feed.restore_cache()
        self.response.set_status(200)
        logging.info("FetchWorker done: " + url)

class FetchAllWorker(webapp.RequestHandler):
    def get(self):
        logging.info("FetchAll")
        for feed in Feed.all():
            logging.info("Adding fetch task for feed " + feed.title)
            taskqueue.add(url="/fetch", params={'url': feed.url})
            taskqueue.add(url="/fetch", params={'url': feed.comments})
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
        

def main():
  application = webapp.WSGIApplication(
                                       [('/', StartPage),
                                        ('/about', AboutPage),
                                        ('/feeds', FeedsPage),
                                        ('/bytype', TypeView),
                                        ('/bychoice', ChoiceView),
                                        ('/bydate', DateView),
                                        #testing 
                                        ('/byranking', RankingView),
                                        ('/database', CsvView),
                                        ('/search', SearchView),
                                        ('/cse-config', CSEConfig),
                                        ('/fetchallsync', FetchAllSyncWorker),
                                        ('/fetchall', FetchAllWorker),
                                        ('/fetch', FetchWorker),
                                        ('/reboot', RebootCommand),
                                        ('/init', InitDatabase),
                                        ('/feed_big', FeedHandler2),
                                        ('/feed_small', FeedHandler1)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
