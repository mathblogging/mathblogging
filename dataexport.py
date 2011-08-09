from main import *

class CsvView(CachedPage):
    cacheName = "CsvView"
    selfurl = "database.csv"
 #   self.response.headers['Content-Type'] = 'text/csv'
    def generatePage(self):
        output = []
        output.append( """title, homepage, person, category, posts_url, comments_url, priority, favicon, listtitle, language""")
        for feed in Feed.gql("WHERE category IN :1 ORDER BY listtitle", ['pure', 'applied', 'teacher', 'history', 'visual','art','journalism','fun','journal', 'general','institution','commercial','community']):
            output.append(""" "%(title)s",%(homepage)s,"%(person)s",%(category)s,%(url)s,%(comments)s,1,%(favicon)s, "%(listtitle)s",%(language)s \n""" % {'title': feed.title,'homepage': feed.homepage, 'person': feed.person , 'category':feed.category, 'url': feed.posts_url,'comments': feed.comments_url, 'favicon': feed.favicon, 'listtitle': feed.listtitle, 'language' : feed.language } )
        return "".join(output)

class OPMLView(CachedPage):
    cacheName = "OPMLView"
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
