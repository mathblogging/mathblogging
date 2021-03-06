from main import *

class StartPage(CachedPage):
    cacheName = "StartPage"
    def generatePage(self):
        output = []
        output.append( '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head>
    <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8"/>
    <link rel="stylesheet" type="text/css" href="/content/site.css"/>
    <link rel="icon" href="/favicon.ico" type="image/x-icon" />
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />
    <style type="text/css">
body {
  height: 600px; 
  background: #DDDDDD;
  background-repeat: repeat-x;
  background-image: url("/content/background-frontpage.png");
  background-image: -webkit-gradient(linear,left top,left bottom, color-stop(0, #444444), color-stop(0.33, #AAAAAA), color-stop(1, #DDDDDD));
  background-image: -moz-linear-gradient(center top , #444444 0%, #AAAAAA 200px, #DDDDDD 100%);
}
h1 {
  margin-bottom: 20px;
}
a {
  padding: 10pt;
}
.footer {
  padding-top: 100px;
}
    </style>
    <title>Mathblogging.org</title>
  </head><body>
<h1 style="text-align:center">Mathblogging.org <span style="font-size: 10pt; color: rgb(204, 204, 204);">your one-stop shop for mathematical blogs</span></h1>


<table style="margin: auto; width: 592px;" border="0" cellpadding="0" cellspacing="0">
<tbody align="center">
<tr align="center">
    <td align="center"><a href="/bydate" ><img src="/content/date-128.png" alt="View the latest posts"/></a><br/><b>View the Latest Posts</b></td>
    <td align="center"><a href="/bytype"><img src="/content/type-128.png" alt="View by type"/></a><br/><b>View by Category</b></td>
    <td align="center"><a href="/bystats"><img src="/content/ranking-128.png" alt="View by stats"/></a><br/><b>View by Stats</b></td>
</tr>
<tr align="center">
    <td align="center" style="padding-top:30px;"><a href="/weekly-picks"><img src="/content/favorites-128.png" alt="View our favorites"/></a><br/><b>Our weekly picks</b></td>
   <td align="center" style="padding-top:30px;"><a href="/planettag"><img src="/content/tag-128.png" alt="View Posts by Tag"/></a><br/><b>View by Tag</b></td>
    <td align="center" style="padding-top:30px;"><a href="/planetmo"><img src="/content/planet-128.png" alt="PlanetMO"/></a><br/><b>PlanetMO</b></td>
</tr>
</tbody></table>


<div style="margin:20px;">

<div id="cse-search-form" style="width: 100%;">Loading custom search. If you don't have JavaScript, you can use <a href="http://www.google.com/cse/home?cx=011837388000883284523:et7bffbfveg">this link</a> to search.</div>
<script src="http://www.google.com/jsapi" type="text/javascript"></script>
<script type="text/javascript">
  google.load('search', '1', {language : 'en', style : google.loader.themes.SHINY});
  google.setOnLoadCallback(function() {
    var customSearchControl = new google.search.CustomSearchControl('011837388000883284523:et7bffbfveg');
    customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
    var options = new google.search.DrawOptions();
    options.setSearchFormRoot('cse-search-form');
    customSearchControl.draw('cse', options);
  }, true);
</script>
<div id="cse-search-form2" style="width: 100%;">
</div>

<div id="cse" style="width:100%;"></div>

<link rel="stylesheet" href="/content/cse-frontpage-2.css" type="text/css" />
</div>

<table style="margin:auto; width: 450px; padding-top:10px;" border="0" cellpadding="0" cellspacing="0">
<tbody align="center">
<tr align="center">
    <td align="center"><a href="https://mathblogging.wordpress.com/contact-us/"><img src="/content/mail-64.png" alt="A blog's not listed?"/></a><br/><span style="font-size:90%">A blog's not listed? <br/> Tell us!</span></td>
    <td align="center"><a href="feeds"><img src="/content/rss-64.png" alt="Grab a feed"/></a><br/><span style="font-size:90%"> Visiting too often? <br/> Grab a feed! </span></td>
    <td align="center"><a href="http://mathblogging.wordpress.com/about"><img src="/content/about-64.png" alt="More about us"/></a><br/><span style="font-size:90%;">More about us? <br/> Visit our blog.</span></td>
</tr>
</tbody>
</table>

<div class="twitter">
<script type="text/javascript" src="http://widgets.twimg.com/j/2/widget.js"></script>
<script>
new TWTR.Widget({
  version: 2,
  type: 'list',
  rpp: 30,
  interval: 6000,
  title: '@mathblogging',
  subject: 'math bloggers on twitter',
  width: 400,
  height: 400,
  theme: {
    shell: {
      background: '#ffffff',
      color: '#000000'
    },
    tweets: {
      background: '#ffffff',
      color: '#000000',
      links: '#878787'
    }
  },
  features: {
    scrollbar: true,
    loop: false,
    live: true,
    hashtags: true,
    timestamp: true,
    avatars: true,
    behavior: 'all'
  }
}).render().setList('mathblogging', 'math-bloggers').start();
</script>
</div>''')
        output.append( footer )
        output.append( """  </body></html> """ )
        return "".join(output)
