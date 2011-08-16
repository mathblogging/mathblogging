from main import *

import counter
        

class PlanetMO(TemplatePage):
    cacheName = "PlanetMO"
    def generateContent(self):
        output = []
        output.append( """<h2> PlanetMO <a href="planetmo-feed"><img src="/content/rss-64.png" alt="PlanetMO feed" height="25"/></a> </h2>

At PlanetMO we collect recent posts tagged "mathoverflow", "math overflow", "mo" or "planetmo".""")

        for entry in Post.gql("WHERE tags IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['Planetmo','Mathoverflow', 'Math Overflow','Mo','MO']):
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
  """ )
            output.append( entry.content )
            output.append( """  </div> </div> """ )
        return "".join(output)
