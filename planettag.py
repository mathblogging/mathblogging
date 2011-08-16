from main import *

import counter
        
memcachekey = "TagListMemCacheKey"

class TagListWorker(webapp.RequestHandler):
    def get(self):
        try:
            logging.info("TagListWorker: generating tag list")
            all_tag = [ tag for entry in Post.all() for tag in entry.tags ]
            common_tags = counter.Counter(all_tag)
            memcache.set(memcachekey, common_tags, 10800)
        except Exception, e:
            self.response.set_status(200)
            logging.warning("TagListWorker failed: \n" + str(e))

class PlanetTag(TemplatePage):
    cacheName = ""
    def generateContent(self):
        tagname = self.request.get('content')
        logging.info("PlanetTag: tagname '" + tagname + "'")
        output = []
        output.append( """<h2> PlanetTAG </h2>

<p> Click on a tag to see a list of recent posts. Right now, you chose <big>==%(tagname)s==</big>.</p>
<p> For convenience, we filter out the dominant tags <a href="/planettag?content=Mathematics">Mathematics</a>, <a href="/planettag?content=Math">Math</a>, <a href="/planettag?content=Maths">Maths</a>, <a href="/planettag?content=Matem&#225;ticas">Matem&#225;ticas</a>, <a href="/planettag?content=Matematica">Matematica</a> and the infamous <a href="/planettag?content=Uncategorized">Uncategorized</a> (as well as some error generating tags). </p>

<div id="tagcloud" style="width: 750px; height: 550px; position: relative;"></div>""" % {"tagname":tagname})
        for entry in Post.gql("WHERE tags = :1 ORDER BY timestamp_created DESC LIMIT 20",tagname):
            output.append( """ <div class="planetbox">  
  <div class="planethead">
  <h2><a href="%(link)s" title="%(title)s">%(title)s</a></h2>
  <div class="planetsubtitle">Posted on <a href="%(homepage)s" title="%(service)s">%(service)s</a> at %(tcreated)s.
  </div>
  <div class="planettags">
     <i>Tags:</i> """ % {"link":entry.link, "title":entry.title, "homepage":entry.homepage, "service":html_escape(entry.service), "tcreated":entry.printShortTime_created()} )
            for tag in entry.tags:
                output.append(tag)
                output.append(", ")
            output.append( """ </div>
  </div>
  <div class="planetbody">
  <p> """ )
            output.append( entry.content )
            output.append( """  </p>  </div> </div>""" )
        output.append( """ 
 <script type="text/javascript">
      /*!
       * Create an array of objects to be passed to jQCloud, each representing a word in the cloud and specifying
       * the following mandatory attributes:
       *
       * text: a string containing the word(s)
       * weight: a number (integer or float) defining the relative importance of the word
       *         (such as the number of occurrencies, etc.). The range of values is arbitrary, as they will
       *         be linearly mapped to a discrete scale from 1 to 10.
       *
       * You can also specify the following optional attributes:
       *
       * url: a URL to which the word will be linked. It will be used as the href attribute of an HTML anchor.
       * title: an HTML title for the span that will contain the word(s)
       */
      var word_list = [ """ )
        taglist = memcache.get(memcachekey)
        logging.info("taglist is " + str(taglist))
        if taglist:
            for tag, weight in memcache.get(memcachekey).iteritems():
                if tag != "Uncategorized" and tag != "Uncategorized>" and tag != "Mathematics" and tag != "Math" and tag != "Maths" and tag != "Http://gdata.youtube.com/schemas/2007#video" and repr(tag) != repr(u'Matem\xe1ticas') and tag != "Matematica" and weight > 10:
                    output.append(""" {text: "%(text)s", weight: %(weight)s, url: "/planettag?content=%(text)s"}, """ % {"text":tag, "weight": weight} )
        output.append( """
      ];
      window.onload = function() {
        // Call jQCloud on a jQuery object passing the word list as the first argument. Chainability of methods is maintained.
        $("#tagcloud").jQCloud(word_list);
      };
    </script>
""" )
        return "".join(output)
