from main import *

class DateViewResearch(TemplatePage):
    cacheName = "DateViewResearch"
    def generateContent(self):
        s = """<div class="tocbox"> 
  <ul>
    <li><a href="/bydate" title="Recent posts">All</a> </li>
    <li><a href="/byresearchdate" title="Recent posts in Research">Researchers</a>
    </li>
    <li><a href="/byartvishisdate" title="Recent posts in Art,Visual,History">Art/Vis/His</a>
    </li>
    <li><a href="/byteacherdate" title="Recent posts from Teachers">Teachers</a>
    </li>
  </ul>
</div>
        <h2> The latests posts 'Pure, Applied' </h2>
<table class="bydate">
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
        for post in Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['pure','applied']):
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
