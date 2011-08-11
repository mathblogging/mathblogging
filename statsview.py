from main import *

class StatsView(TemplatePage):
    cacheName = "StatsView"
    def generateContent(self):
       output = []
       output.append("""
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
            <tbody>""")
       for feed in Feed.gql("WHERE category IN :1 ORDER BY comments_day DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(comments_day)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_day': str(feed.comments_day), 'homepage': feed.homepage, 'title': html_escape(feed.title) })
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
       for feed in Feed.gql("WHERE category IN :1 ORDER BY comments_week DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(comments_week)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_week': str(feed.comments_week), 'homepage': feed.homepage, 'title': html_escape(feed.title) })
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
       for feed in Feed.gql("WHERE category IN :1 ORDER BY posts_week DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_week)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_week': str(feed.posts_week), 'homepage': feed.homepage, 'title': html_escape(feed.title) })
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
       for feed in Feed.gql("WHERE category IN :1 ORDER BY posts_month DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_month)s
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_month': str(feed.posts_month), 'homepage': feed.homepage, 'title': html_escape(feed.title) })
       output.append("""
              </tbody>
           </table>""")
       return "".join(output)
       


