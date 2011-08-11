from main import *

class StatsView(TemplatePage):
    cacheName = "StatsView"
    def generateContent(self):
       output = []
       output.append("""
       <div class="content">
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
                       %(comments_day)i
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_day': feed.comments_day, 'homepage': feed.homepage, 'title': feed.title })
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
                       %(comments_week)i
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'comments_week': feed.comments_week, 'homepage': feed.homepage, 'title': feed.title })
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
       for feed in Feed.gql("WHERE category IN :1 ORDER BY posts_day DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_week)i
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_week': feed.posts_week, 'homepage': feed.homepage, 'title': feed.title })
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
       for feed in Feed.gql("WHERE category IN :1 ORDER BY posts_day DESC", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
          output.append("""
                 <tr>
                    <td valign="bottom" class="datecolumn">
                       %(posts_month)i
                    </td>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                 </tr>""" % {'posts_month': feed.posts_month, 'homepage': feed.homepage, 'title': feed.title })
       output.append("""
              </tbody>
           </table>""")
       return "".join(output)
       


