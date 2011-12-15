from main import *


class StatsViewBase(TemplatePage):
    def generateContent(self):
       output = []
       output.append("""
            <div class="tocbox"> 
		  <ul>
		    <li><a href="/bystats" title="Recent stats">All</a> </li>
		    <li><a href="/bystats-researchers" title="Recent stats for Researchers">Researchers</a>
		    </li>
		    <li><a href="/bystats-educators" title="Recent stats for Educators">Educators</a>
		    </li>
		    <li><a href="/bystats-artvis" title="Recent stats for Art, Visual">Art/Visual</a>
		    </li>
		  </ul>
		</div>
        <h2> The latests stats %(title)s </h2>
            <table class="bydate" id="commentsperday">
                <thead>
                    <tr>
                        <th align="left" class="datecolumn">
                        </th>
                        <th align="left" class="blogcolumn">
                            Comments last 24h
                        </th>
                    </tr>
                </thead>
            <tbody>"""% {'title':html_escape(self.selftitle)})
       for feed in self.query():
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(comments_day)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_day': str(feed.comments_day), 'homepage': html_escape(feed.homepage), 'title': html_escape(feed.title) })
       output.append("""
              </tbody>
           </table>""")

       output.append("""
           <table class="bydate" id="commentsperweek">
              <thead>
                 <tr>
                    <th align="left" class="datecolumn">
                    </th>
                    <th align="left" class="blogcolumn">
                       Comments last week
                    </th>
                 </tr>
              </thead>
              <tbody>""")
       for feed in self.query():
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(comments_week)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_week': str(feed.comments_week), 'homepage': html_escape(feed.homepage), 'title': html_escape(feed.title) })
       output.append("""
              </tbody>
           </table>""")

       output.append("""
           <table class="bydate" id="postsperweek">
              <thead>
                 <tr>
                    <th align="left" class="datecolumn">
                    </th>
                    <th align="left" class="blogcolumn">
                       Posts last week
                    </th>
                 </tr>
              </thead>
              <tbody>""")
       for feed in self.query():
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_week)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_week': str(feed.posts_week), 'homepage': html_escape(feed.homepage), 'title': html_escape(feed.title) })
       output.append("""
              </tbody>
           </table>""")

       output.append("""
           <table class="bydate" id="postspermonth">
              <thead>
                 <tr>
                    <th align="left" class="datecolumn">
                    </th>
                    <th align="left" class="blogcolumn">
                       Posts last month
                    </th>
                 </tr>
              </thead>
              <tbody>""")
       for feed in self.query():
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_month)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_month': str(feed.posts_month), 'homepage': html_escape(feed.homepage), 'title': html_escape(feed.title) })
       output.append("""
              </tbody>
           </table>""")
       return "".join(output)
       
class StatsView(StatsViewBase):
    selfurl = "bystats"
    selftitle = ""
    cacheName = "StatsView"
    def query(self):
        return Feed.gql("WHERE category IN :1 ORDER BY comments_day DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism'])

class StatsViewResearchers(StatsViewBase):
    selfurl = "bystats-researchers"
    selftitle = " for researchers"
    cacheName = "StatsViewResearchers"
    def query(self):
        return Feed.gql("WHERE category IN :1 ORDER BY comments_day DESC", ['history','pure','applied','general'])

class StatsViewEducators(StatsViewBase):
    selfurl = "bystats-educators"
    selftitle = " for educators"
    cacheName = "StatsViewEducators"
    def query(self):
        return Feed.gql("WHERE category IN :1 ORDER BY comments_day DESC", ['teacher'])

class StatsViewArtVis(StatsViewBase):
    selfurl = "bystats-artvis"
    selftitle = " for art and visual"
    cacheName = "StatsViewArtVis"
    def query(self):
        return Feed.gql("WHERE category IN :1 ORDER BY comments_day DESC", ['art','visual'])

