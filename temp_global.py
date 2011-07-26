header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8"/>
    <link rel="stylesheet" type="text/css" href="/content/site.css"/>
    <link rel="icon" href="/favicon.ico" type="image/x-icon" />
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />
    <title>Mathblogging.org</title>
    <script type="text/javascript" src="/content/jquery-1.5.2.min.js"></script>         
    <link rel="stylesheet" type="text/css" href="/content/jqcloud.css" />
    <script type="text/javascript" src="/content/jqcloud-0.2.1.js"></script>
  </head>
  <body>
    <h1> <a style="text-decoration:none;color:white;" href="/">Mathblogging.org <small style="color: #CCC">beta</small></a></h1>
"""

menu = """
<!-- Top Navigation -->
<div id="menu">
<ul>
  <li><h2><a href="/bydate" title="Recent posts">Posts</a></h2>
  <ul>
    <li><h2><a href="/byresearchdate" title="Recent posts in Research">Researchers</a></h2>
    </li>
    <li><h2><a href="/byartvishisdate" title="Recent posts in Art,Visual,History">Art/Visual/History</a></h2>
    </li>
    <li><h2><a href="/byteacherdate" title="Recent posts from Teachers">Teachers</a></h2>
    </li>
  </ul>
  </li>
  <li><h2><a href="/bytype" title="Blogs by Category">Blogs</a></h2>
  </li>
  <li><h2><a href="/bystats" title="Recent statistics">Stats</a></h2>
  </li>
  <li><h2><a href="/weekly-picks" title="Our weekly picks">Weekly Picks</a></h2>
  </li>     
  <li><h2><a href="/planettag" title="PlanetTAG">PlanetTAG</a></h2>
  </li>
  <li><h2><a href="/planetmo" title="PlanetMO">PlanetMO</a></h2>
  </li>     
  <li><h2><a href="/feeds" title="Feeds">Feeds</a></h2>
  </li>
  <li><h2><a href="https://mathblogging.wordpress.com/" title="About us">About us</a></h2>
  </li>
  <li><h2><a href="/" title="Search">Search</a></h2>
  </li>
</ul>						
</div>
<!-- end Top Navigation -->
"""

disqus = """
<!-- disqus code-->
<div class="disqus">
<hr/>
<div id="disqus_thread"></div>
<script type="text/javascript">
    /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
    var disqus_shortname = 'mathblogging'; // required: replace example with your forum shortname

    // The following are highly recommended additional parameters. Remove the slashes in front to use.
    // var disqus_identifier = 'unique_dynamic_id_1234';
    // var disqus_url = 'http://example.com/permalink-to-page.html';

    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
<noscript><p>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></p></noscript>
<a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
</div>
<!-- end disqus code-->
"""

footer = """
<!-- copyright footer -->
<div class="footer">
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">
  <img alt="Creative Commons License" src="http://i.creativecommons.org/l/by-nc-sa/3.0/80x15.png"/>
</a>
<p>
mathblogging.org is licensed under a <br/> <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/3.0/">Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License</a>.
</p>
</div>
<!-- end copyright footer -->
"""
