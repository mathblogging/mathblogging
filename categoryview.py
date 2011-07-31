from main import *

class CategoryView(TemplatePage):
    cacheName = "CategoryView"
    def generateSection(self,pair):
        caption = pair[0]
        categorylabel = pair[1]
        output = []
        output.append("""<h2 id="%(category)s"> %(caption)s <font size="-1"> <a href="#"> (Back to top) </a> </font> </h2> <ul class="feedbox-list"> """ % {'category': categorylabel, 'caption': caption})
        for feed in Feed.gql("WHERE category = :1 ORDER BY listtitle", categorylabel):
            output.append("""<li>
	  <div class="feedbox">
            <h3> <a href="%(homepage)s">%(title)s </a> </h3>
<!-- HIER STAND MAL EIN IF GEGEN LEERE ULs -->
	    <ul>""" % { 'homepage': feed.homepage, 'title': feed.title })
            for entry in Post.gql("WHERE service = :1 ORDER BY timestamp_created DESC LIMIT 7", feed.title):
                output.append("""<li><a href="%(link)s" title="%(title)s">%(title)s</a></li>""" % {'link': entry.link, 'title': entry.title})
	    output.append("</ul>")
        output.append("</div> </li> </ul>")
        return "".join(output)
    def generateContent(self):
        s = """
<p> The categories represent what we see as roughly the primary focus of each blog -- this supplements <a href="/planettag">PlanetTAG</a>.</p>

<div class="tocbox"> 
<ul>
<li> <a href="#pure">Pure</a></li> 
<li> <a href="#applied">Applied</a></li> 
<li> <a href="#teacher">Teachers</a></li> 
<li> <a href="#visual">Visualization</a></li> 
<li> <a href="#history">History</a></li> 
<li> <a href="#art">Art</a></li> 
<li> <a href="#fun">Fun</a></li> 
<li> <a href="#general">General</a></li> 
<li> <a href="#journalism">Journalism</a></li>
<li> <a href="#journal">Journals</a></li> 
<li> <a href="#commercial">Commercial</a></li> 
<li> <a href="#community">Communities</a></li> 
<li> <a href="#institution">Institutions</a></li> 
<li> <a href="#news">News</a></li> 
<li> <a href="#carnivals">Carnivals</a></li> 
</ul>
</div>"""
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
            ['Institutions','institution'],
            ['News','news'],
            ['Carnivals','carnival'],
        ]
        return s + " ".join([self.generateSection(pair) for pair in thelist])
