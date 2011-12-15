from main import *
from django.utils import simplejson

class CsvView(CachedPage):
    cacheName = "CsvView"
    mimeType = "text/csv"
    selfurl = "database.csv"
    def generatePage(self):
        output = []
        output.append( """title, homepage, person, category, posts_url, comments_url, priority, favicon, listtitle, language""")
        for feed in Feed.gql("WHERE category IN :1 ORDER BY listtitle", ['pure', 'applied', 'teacher', 'history', 'visual','art','journalism','fun','journal', 'general','institution','commercial','community']):
            output.append(""" "%(title)s",%(homepage)s,"%(person)s",%(category)s,%(url)s,%(comments)s,1,%(favicon)s, "%(listtitle)s",%(language)s \n""" % {'title': feed.title,'homepage': feed.homepage, 'person': feed.person , 'category':feed.category, 'url': feed.posts_url,'comments': feed.comments_url, 'favicon': feed.favicon, 'listtitle': feed.listtitle, 'language' : feed.language } )
        return "".join(output)

class OPMLView(CachedPage):
    cacheName = "OPMLView"
    mimeType = "application/xml"
    selfurl = "database-opml.xml"
    def generatePage(self):
        output = []
        output.append("""<?xml version="1.0" encoding="UTF-8"?> <opml version="1.0">
 <head>
        <title>Mathblogging.org Database export to OPML</title>
    </head>
    <body><outline title="Mathblogging.org" text="Mathblogging.org">""")
        for feed in Feed.gql("WHERE category IN :1 ORDER BY listtitle", ['pure', 'applied', 'teacher', 'history', 'visual','art','journalism','fun','journal', 'general','institution','commercial','community']):
            output.append(""" 
            <outline text="%(title)s" title="%(title)s" type="rss"
                xmlUrl="%(url)s" htmlUrl="%(homepage)s"/>""" % {'title': feed.title,'homepage': feed.homepage, 'person': feed.person , 'category':feed.category, 'url': feed.posts_url,'comments': feed.comments_url, 'favicon': feed.favicon, 'listtitle': feed.listtitle, 'language' : feed.language } )
        output.append("""</outline></body></opml>""")
        return "".join(output)

class CSEConfig(CachedPage):
    cacheName = "CSEConfig"
    mimeType = "application/xml"
    def generatePage(self):
        output = []
        output.append( """<?xml version="1.0" encoding="UTF-8" ?>
        <Annotations>""")
        for feed in Feed.all():
            output.append( """
                <Annotation about="%(homepage)s*">
                     <Label name="_cse_et7bffbfveg"/>
                </Annotation>
                """ % {'homepage': add_slash(strip_http(feed.homepage)) } )
        output.append("""</Annotations>""")
        return "".join(output)

class PostsJSONExport(CachedPage):
    cacheName = "PostsJSONExport"
    mimeType = "application/json"
    def generatePage(self):
        posts = []
        for post in Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
            posts.append({
                    "title": post.title,
                    "date": post.timestamp_created.strftime('%B %d,%Y %I:%M:%S %p'),
                    "length": post.length,
                    "blog": post.service,
                    "tags": [tag for tag in post.tags],
                    "category": post.category,
                    "comments": 0 #TODO
                })
        output = {"posts":posts}
        return simplejson.dumps(output)

class JSONPHandler(CachedPage):
    mimeType = "application/javascript"
    def post_process_content(self, content):
        callback = self.request.get("callback")
        logging.info("Add JSONP padding: " + callback)
        return "%s(%s);" % (callback, content)

class WeeklyPicksJSONPHandler(JSONPHandler):
    cacheName = "WeeklyPicksJSONPHandler"
    def generatePage(self):
        picks = [ {
            "url": "http://rjlipton.wordpress.com/2011/12/03/the-meaning-of-omega/", 
            "caption": "If you haven't followed the debate on TCS breakthrough in matrix multiplication, you can read up on it at Godel's Lost Letter and P=NP (and you might also check out a short comment at Yet Another Math Programmer)." } ]
        output = picks
        return simplejson.dumps(output)
    

