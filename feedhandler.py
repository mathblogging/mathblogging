from main import *

class FeedHandlerBase(CachedPage):
    selfurl = "feed"
    def generatePage(self):
        output = []
        output.append( """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>Mathblogging.org</title>
 <link href="http://www.mathblogging.org/%(url)s" rel="self"/>
 <link href="http://www.mathblogging.org/"/>
 <updated>2010-11-10T21:50:23-05:00</updated>
 <id>http://www.mathblogging.org/</id>
 <author>
   <name>mathblogging.org</name>
   <email>mathblogging.network@gmail.com</email>
 </author>""" % {'url':self.selfurl})
        for entry in self.query():
            output.append(""" <entry>
   <title> [[%(service)s]] %(title)s </title>
   <author>
      <name>%(service)s</name>
      <uri>%(homepage)s</uri>
   </author>

   <link href="%(link)s"/>
   <published>%(tcreated)s</published>
   <updated>%(tupdated)s</updated>
   <id>%(link)s</id>
   <content type="html"> Length: approx %(length)d words. </content>
 </entry>""" % {'service': entry.service,'title': entry.title, 'homepage': entry.homepage , 'link':entry.link, 'tcreated': entry.printTime_created_rfc3339(), 'tupdated':entry.printTime_updated_rfc3339(), 'length': entry.length/5} )
        output.append("</feed>")
        return "".join(output)

       
class FeedHandlerAll(FeedHandlerBase):
    selfurl = "feed_all"
    cacheName = "FeedAll"
    def query(self):
        return Post.gql("ORDER BY timestamp_created DESC LIMIT 150")

class FeedHandlerCategory(FeedHandlerBase):
    def query(self):
        return Post.gql("WHERE category = :1 ORDER BY timestamp_created DESC LIMIT 150", self.thecategory)

class FeedHandlerCategories(FeedHandlerBase):
    def query(self):
        return Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", self.thecategories)

class PlanetMOfeed(FeedHandlerBase):
    selfurl = ""
    cacheName = "PlanetMOfeed"
    def query(self):
        return Post.gql("WHERE tags IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['Planetmo','Mathoverflow', 'Math Overflow','Mo','MO'])

class FeedHandlerResearchers(FeedHandlerCategories):
    selfurl = "feed_researchers"
    cacheName = "FeedResearchers"
    thecategories = ['pure','applied','history']

class FeedHandlerPure(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedPure"
    thecategory = "pure"

class FeedHandlerApplied(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedApplied"
    thecategory = "applied"

class FeedHandlerHistory(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedHistory"
    thecategory = "history"

class FeedHandlerVisual(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedVisual"
    thecategory = "visual"

class FeedHandlerArt(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedArt"
    thecategory = "art"

class FeedHandlerFun(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedFun"
    thecategory = "fun"

class FeedHandlerGeneral(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedGeneral"
    thecategory = "general"

class FeedHandlerJournals(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedJournals"
    thecategory = "journal"

class FeedHandlerTeachers(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedTeachers"
    thecategory = "teacher"

class FeedHandlerJournalism(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedJournalism"
    thecategory = "journalism"

class FeedHandlerInstitutions(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedInstitutions"
    thecategory = "institution"

class FeedHandlerCommunities(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedCommunities"
    thecategory = "community"

class FeedHandlerCommercial(FeedHandlerCategory):
    selfurl = ""
    cacheName = "FeedCommercial"
    thecategory = "commercial"

class FeedHandlerPeople(FeedHandlerCategories):
    selfurl = ""
    cacheName = "FeedPeople"
    thecategories = ["pure","applied","visual","history","fun","teacher","journalism","general","art"]
