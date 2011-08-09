from main import *

class GridView(CachedPage):
    cacheName = "NewCategoryView"
    def generateSection(self,pair):
        caption = pair[0]
        categorylabel = pair[1]
        output = []
        output.append(""" <div class="info-col"> 
        <h2 id="%(category)s">  %(caption)s <font size="-1"> </h2>
        <a class="image superman" href="http://jprart.deviantart.com/art/Batman-and-Superman-64545242">View Image</a> 
        <dl>""" % {'category': categorylabel, 'caption': caption})
        for feed in Feed.gql("WHERE category = :1 ORDER BY listtitle", categorylabel):
            output.append(""" <dt> %(title)s </dt>""" % { 'homepage': feed.homepage, 'title': feed.title })
            for entry in Post.gql("WHERE service = :1 ORDER BY timestamp_created DESC LIMIT 7", feed.title):
                output.append("""<dd><a href="%(link)s" title="%(title)s">%(title)s</a></dd>""" % {'link': entry.link, 'title': entry.title})
	    output.append(" ")
        output.append("</dl> </div>")
        return "".join(output)
    def generatePage(self):
        s = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
      <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />

     <title>Categories Grid</title>

     <link rel='stylesheet' type='text/css' href='content/infogrid-style.css' />
    <script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js'></script>
    <script type='text/javascript' src='content/infogrid.js'></script>   
</head> <body> <div id="page-wrap"> """
        thelist = [ 
            ['Pure mathematics', 'pure'],
            ['Applied mathematics','applied'],
            ['Teachers and Educators','teacher'],
            ['Visualizations','visual'],
            ['History','history'],
            ['Art','art'],
            ['Comics, recreational mathematics and other fun','fun'],
            ['General scientific interest','general'],
            ['Journalistic Writers','journalism'],
            ['Journals, Publishers and similar feeds','journal'],
            ['Commercial blogs','commercial'],
            ['Communities','community'],
            ['Institutions','institution']
        ]
        return s + " ".join([self.generateSection(pair) for pair in thelist]) + """</div> </body> </html>"""
