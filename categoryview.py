from main import *

        
class CategoryViewBase(TemplatePage):
    def generateContent(self):
       output = []
       output.append("""
        <p> The categories represent what we see as roughly the primary focus of each blog -- this supplements <a href="/planettag">PlanetTAG</a>.</p>
        <div class="tocbox"> 
        <ul>
        <li> <a href="/bytype-pure">Pure</a></li> 
        <li> <a href="/bytype-applied">Applied</a></li> 
        <li> <a href="/bytype-teacher">Teachers</a></li> 
        <li> <a href="/bytype-visual">Visualization</a></li> 
        <li> <a href="/bytype-history">History</a></li> 
        <li> <a href="/bytype-art">Art</a></li> 
        <li> <a href="/bytype-fun">Fun</a></li> 
        <li> <a href="/bytype-general">General</a></li> 
        <li> <a href="/bytype-journalism">Journalism</a></li>
        <li> <a href="/bytype-journals">Journals</a></li> 
        <li> <a href="/bytype-commercial">Commercial</a></li> 
        <li> <a href="/bytype-communities">Communities</a></li> 
        <li> <a href="/bytype-institutions">Institutions</a></li> 
        <li> <a href="/bytype-news">News</a></li> 
        <li> <a href="/bytype-carnivals">Carnivals</a></li> 

        </ul>
        </div> <br></br>
        <h2 id="%(category)s"> %(caption)s </h2> 
        <ul class="feedbox-list">
        """ % {'category': self.categorylabel(), 'caption': self.caption()})
       for feed in Feed.gql("WHERE category = :1 ORDER BY listtitle", self.categorylabel()):
            output.append("""
            <li>
            <div class="feedbox">
            <h3> <a href="%(homepage)s">%(title)s </a> </h3>
	    <ul>
            """ % { 'homepage': feed.homepage, 'title': html_escape(feed.title) })
            for entry in Post.gql("WHERE homepage = :1 ORDER BY timestamp_created DESC LIMIT 7", feed.homepage):
                output.append("""
                <li><a href="%(link)s" title="%(title)s">%(title)s</a></li>
                """ % {'link': html_escape(entry.link), 'title': html_escape(entry.title)})
            output.append("""
            </ul> </div> </li>
            """)
       output.append("""
	</ul>
	""")
       return "".join(output)


class CategoryView(TemplatePage):
    selfurl = "bytype"
    selftitle = ""
    cacheName = "CategoryView"
    def generateContent(self):
       return """
        <p> The categories represent what we see as roughly the primary focus of each blog -- this supplements <a href="/planettag">PlanetTAG</a>.</p>
        <div class="tocbox"> 
        <ul>
        <li> <a href="/bytype-pure">Pure</a></li> 
        <li> <a href="/bytype-applied">Applied</a></li> 
        <li> <a href="/bytype-teacher">Teachers</a></li> 
        <li> <a href="/bytype-visual">Visualization</a></li> 
        <li> <a href="/bytype-history">History</a></li> 
        <li> <a href="/bytype-art">Art</a></li> 
        <li> <a href="/bytype-fun">Fun</a></li> 
        <li> <a href="/bytype-general">General</a></li> 
        <li> <a href="/bytype-journalism">Journalism</a></li>
        <li> <a href="/bytype-journal">Journals</a></li> 
        <li> <a href="/bytype-commercial">Commercial</a></li> 
        <li> <a href="/bytype-community">Communities</a></li> 
        <li> <a href="/bytype-institution">Institutions</a></li> 
        <li> <a href="/bytype-news">News</a></li> 
        <li> <a href="/bytype-carnivals">Carnivals</a></li> 

        </ul>
        </div>"""

class CategoryViewPure(CategoryViewBase):
    selfurl = "bytype-pure"
    selftitle = ""
    cacheName = "CategoryViewPure"
    def categorylabel(self):
        return 'pure'
    def caption(self):
        return 'Pure mathematics'

class CategoryViewApplied(CategoryViewBase):
    selfurl = "bytype-applied"
    selftitle = ""
    cacheName = "CategoryViewApplied"
    def categorylabel(self):
        return 'applied'
    def caption(self):
        return 'Applied mathematics'

class CategoryViewTeacher(CategoryViewBase):
    selfurl = "bytype-teacher"
    selftitle = ""
    cacheName = "CategoryViewTeacher"
    def categorylabel(self):
        return 'teacher'
    def caption(self):
        return 'Teachers and Educators'

class CategoryViewVisual(CategoryViewBase):
    selfurl = "bytype-visual"
    selftitle = ""
    cacheName = "CategoryViewVisual"
    def categorylabel(self):
        return 'visual'
    def caption(self):
        return 'Visualizations'
        
class CategoryViewHistory(CategoryViewBase):
    selfurl = "bytype-history"
    selftitle = ""
    cacheName = "CategoryViewHistory"
    def categorylabel(self):
        return 'history'
    def caption(self):
        return 'History'
        
class CategoryViewArt(CategoryViewBase):
    selfurl = "bytype-art"
    selftitle = ""
    cacheName = "CategoryViewArt"
    def categorylabel(self):
        return 'art'
    def caption(self):
        return 'Art'
        
class CategoryViewFun(CategoryViewBase):
    selfurl = "bytype-fun"
    selftitle = ""
    cacheName = "CategoryViewFun"
    def categorylabel(self):
        return 'fun'
    def caption(self):
        return 'Comics, recreational mathematics and other fun'
        
class CategoryViewGeneral(CategoryViewBase):
    selfurl = "bytype-general"
    selftitle = ""
    cacheName = "CategoryViewGeneral"
    def categorylabel(self):
        return 'general'
    def caption(self):
        return 'General scientific interest'
        
class CategoryViewJournalism(CategoryViewBase):
    selfurl = "bytype-journalism"
    selftitle = ""
    cacheName = "CategoryViewJournalism"
    def categorylabel(self):
        return 'journalism'
    def caption(self):
        return 'Journalistic Writers'
        
class CategoryViewJournals(CategoryViewBase):
    selfurl = "bytype-journals"
    selftitle = ""
    cacheName = "CategoryViewJournals"
    def categorylabel(self):
        return 'journal'
    def caption(self):
        return 'Journals'
        
class CategoryViewCommercial(CategoryViewBase):
    selfurl = "bytype-commercial"
    selftitle = ""
    cacheName = "CategoryViewCommercial"
    def categorylabel(self):
        return 'commercial'
    def caption(self):
        return 'Commercial blogs'
        
class CategoryViewCommunities(CategoryViewBase):
    selfurl = "bytype-communities"
    selftitle = ""
    cacheName = "CategoryViewCommunities"
    def categorylabel(self):
        return 'community'
    def caption(self):
        return 'Communities'
        
class CategoryViewInstitutions(CategoryViewBase):
    selfurl = "bytype-institutions"
    selftitle = ""
    cacheName = "CategoryViewInstitutions"
    def categorylabel(self):
        return 'institution'
    def caption(self):
        return 'Institutions'

class CategoryViewNews(CategoryViewBase):
    selfurl = "bytype-news"
    selftitle = ""
    cacheName = "CategoryViewNews"
    def categorylabel(self):
        return 'news'
    def caption(self):
        return 'News'

class CategoryViewCarnivals(CategoryViewBase):
    selfurl = "bytype-carnivals"
    selftitle = ""
    cacheName = "CategoryViewCarnivals"
    def categorylabel(self):
        return 'carnival'
    def caption(self):
        return 'Carnivals'