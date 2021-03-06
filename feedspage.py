from main import *

class FeedsPage(TemplatePage):
    cacheName = "FeedsPage"
    def generateContent(self):
        output = []
        output.append( """
<div class="content">

      <h2> The Feeds </h2>
    <p>We offer some very simplistic feeds since the primary purpose of mathblogging.org is to help you find blogs, not to bundle them. <br/> There are much better tools around if you want to generate a metafeed of your favorite feeds; e.g., google reader, friendfeed, facebook etc.</p>
    <p> You can also <a href="/database-opml.xml">download our OPML-file</a> to import our database into your feed reader or <a href="/database.csv"> get our database as a csv</a>. </p>

      <ul>
	    <li> <b> The feeds by category</b> </li>
	    <li> </li>
	    <li> <a href="/feed_pure">The pure feed</a> </li>
	    <li> <a href="/feed_applied">The applied feed</a> </li>
	    <li> <a href="/feed_teachers">The teachers feed</a> </li>
	    <li> <a href="/feed_visual">The visual feed</a> </li>
	    <li> <a href="/feed_history">The history feed</a> </li>
	    <li> <a href="/feed_art">The art feed</a> </li>
	    <li> <a href="/feed_fun">The fun feed</a> </li>
	    <li> <a href="/feed_general">The general feed</a> </li>
	    <li> <a href="/feed_journalism">The journalism feed</a> </li>
	    <li> <a href="/feed_journals">The journals feed</a> </li>
	    <li> <a href="/feed_commercial">The commercial feed</a> </li>
	    <li> <a href="/feed_institutions">The institutions feed</a> </li>
	    <li> <a href="/feed_communities">The communities feed</a> </li>
	    <li> <a href="/feed_newssite">The news-sites feed</a> </li>
	    <li> <a href="/feed_carnival">The carnival feed</a> </li>
      </ul>
      <ul>
	    <li> <b>Some mixed feeds</b> </li> 
	    <li> </li>
	    <li> <a href="/feed_researchers">The researchers feed</a> (pure, applied and history)</li> 
	    <li> <a href="/feed_people">The people feed (everything but institutions, communities, journals, commercial)</a> </li>
	    <li> <a href="/feed_all">The full feed</a> </li>
      </ul>
      </div>
      """)
        return "".join(output)
