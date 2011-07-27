from main import *

class DateViewTeacher(TemplatePage):
    cacheName = "DateViewTeacher"
    def generateContent(self):
        s = """<h2> The latests posts Teachers and Educators </h2>
<table id="postsbydate">
  <thead>
  <tr>
    <th align="left" class="datecolumn">
      Date
    </th>
    <th align="left" class="blogcolumn">
      Blog
    </th>
    <th align="left" class="postcolumn">
      Post
    </th>
  </tr>
  </thead>
  <tbody>"""
        for post in Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['teacher']):
            s = s + """
  <tr>
    <td valign="bottom" class="datecolumn">
      <div>
        %(time)s
      </div>
    </td>
    <td valign="bottom" class="blogcolumn">
      <div>
	<a href="%(homepage)s" title="%(service)s">%(service)s</a>
      </div>
    </td>
    <td valign="bottom" class="postcolumn">
      <div>
	<a href="%(link)s" title="%(title)s">%(title)s</a>
      </div>
    </td>
  </tr>""" % {'time': post.printShortTime_created(), 'homepage': post.homepage, 'service': post.service, 'title': post.title, 'link': post.link }
        return s + "</tbody></table>"
