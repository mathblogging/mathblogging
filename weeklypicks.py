from main import *

class WeeklyPicks(TemplatePage):
    cacheName = "WeeklyPicks"
    def generateContent(self):
        output = []
        output.append( """<h2> Weekly picks <a href="https://mathblogging.wordpress.com/category/weekly-picks/feed/"><img src="/content/rss-64.png" alt="Weekly picks" height="25"/></a> </h2>

Our weekly picks, crossposted from <a href="https://mathblogging.wordpress.com/category/weekly-picks/">Mathblogging.org -- the blog</a>.
""")

        for entry in Post.gql("WHERE tags IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['Weekly Picks']):
            output.append( """ <div class="planetbox">  
  <div class="planethead">
  <h2><a href="%(link)s" title="%(title)s">%(title)s</a></h2>
  <div class="planetsubtitle">Posted %(tcreated)s.
  </div>
  <div class="planettags"> """ % {"link":html_escape(entry.link), "title":html_escape(entry.title), "homepage":html_escape(entry.homepage), "tcreated":entry.printShortTime_created()} )
            output.append( """ </div>
  </div>
  <div class="planetbody">
  <p> """ )
            output.append( entry.content )
            output.append( """  </p>  </div> </div> """ )
        return "".join(output)
