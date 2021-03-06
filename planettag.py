from main import *


        
class PlanetTag(TemplatePage):
    cacheName = ""
    def generateContent(self):
        list_blob = Stored_List.gql("WHERE name = 'Global_Weighted_Taglist'").get()
        weighted_taglist = list_blob.content
        tagname = self.request.get('content')
        output = []
        output.append( """
            <h2> PlanetTAG </h2>
            <p> Click on a tag to see a list of recent posts. Right now, you chose <big>==%(tagname)s==</big>.</p>
            <p> For convenience, we filter out the dominant tags <a href="/planettag?content=Mathematics">Mathematics</a>, <a href="/planettag?content=Math">Math</a>, <a href="/planettag?content=Maths">Maths</a>, <a href="/planettag?content=Matem&#225;ticas">Matem&#225;ticas</a>, <a href="/planettag?content=Matematica">Matematica</a> and the infamous <a href="/planettag?content=Uncategorized">Uncategorized</a> (as well as some error generating tags). </p>
            <p>
            You can also use the Custom Google Search underneath the tag cloud for a full text search through all blogs.
            </p>

           <div id="tagcloud" style="width: 750px; height: 550px; position: relative;"></div>""" % {"tagname":tagname})
        for entry in Post.gql("WHERE tags = :1 ORDER BY timestamp_created DESC LIMIT 20",tagname):
            output.append( """ 
            <div class="planetbox">  
            <div class="planethead">
            <h2><a href="%(link)s" title="%(title)s">%(title)s</a></h2>
            <div class="planetsubtitle">Posted on <a href="%(homepage)s" title="%(service)s">%(service)s</a> at %(tcreated)s.
            </div> 
            <div class="planettags">
            <i>Tags:</i> """ % {"link":entry.link, "title":entry.title, "homepage":entry.homepage, "service":html_escape(entry.service), "tcreated":entry.printShortTime_created()} )
            for tag in entry.tags:
                output.append(tag)
                output.append(", ")
            output.append( """ 
            </div>
            </div>
            <div class="planetbody">
            <p> """ )
            output.append( truncate_html_words(entry.content,100) )
            output.append( """  </p>  </div> </div>""" )
        output.append( """ 
        <script type="text/javascript"> 
        /*!
       * Create an array of objects to be passed to jQCloud, each representing a word in the cloud and specifying
       * the following mandatory attributes:
       *
       * text: a string containing the word(s)
       * weight: a number (integer or float) defining the relative importance of the word
       *         (such as the number of occurrencies, etc.). The range of values is arbitrary, as they will
       *         be linearly mapped to a discrete scale from 1 to 10.
       *
       * You can also specify the following optional attributes:
       *
       * url: a URL to which the word will be linked. It will be used as the href attribute of an HTML anchor.
       * title: an HTML title for the span that will contain the word(s)
       */
       var word_list = [ """ )
        for tag_weight in weighted_taglist:
            if tag_weight[0] != "Uncategorized" and tag_weight[0] != "Uncategorized>" and tag_weight[0] != "Mathematics" and tag_weight[0] != "Math" and tag_weight[0] != "Maths" and tag_weight[0] != "Http://gdata.youtube.com/schemas/2007#video" and repr(tag_weight[0]) != repr(u'Matem\xe1ticas') and tag_weight[0] != "Matematica" and tag_weight[1]>10 :
               output.append(""" {text: "%(text)s", weight: %(weight)s, url: "/planettag?content=%(text)s"}, """ % {"text":html_escape(tag_weight[0]), "weight": tag_weight[1] } )
        output.append( """
        ];
        window.onload = function() {
        // Call jQCloud on a jQuery object passing the word list as the first argument. Chainability of methods is maintained.
        $("#tagcloud").jQCloud(word_list);
        };
        </script>
            <div style="margin:20px;">

            <div id="cse-search-form" style="width: 100%;">
            Loading custom search. If you don't have JavaScript, you can use <a href="http://www.google.com/cse/home?cx=011837388000883284523:et7bffbfveg">this link</a> to search.
            </div>
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
        """ )
        return "".join(output)

class PlanetTagBlogs(TemplatePage):
    cacheName = ""
    def generateContent(self):
        list_blob = Stored_List.gql("WHERE name = 'Global_Weighted_Taglist'").get()
        weighted_taglist = list_blob.content
        tagname = self.request.get('content')
        output = []
        output.append( """
            <h2> PlanetTAG </h2>
            <p> Click on a tag to see a list of blogs that use the tag. Right now, you chose <big>==%(tagname)s==</big>.</p>
            <p> For convenience, we filter out the dominant tags <a href="/planettag?content=Mathematics">Mathematics</a>, <a href="/planettag?content=Math">Math</a>, <a href="/planettag?content=Maths">Maths</a>, <a href="/planettag?content=Matem&#225;ticas">Matem&#225;ticas</a>, <a href="/planettag?content=Matematica">Matematica</a> and the infamous <a href="/planettag?content=Uncategorized">Uncategorized</a> (as well as some error generating tags). </p>
            <p>
            You can also use the Custom Google Search underneath the tag cloud for a full text search through all blogs.
            </p> """ % {"tagname":tagname})

        output.append("""
            <table class="bydate" id="commentsperday">
                <thead>
                    <tr>
                        <th align="left" class="datecolumn">
                            Blog //
                        </th>
                        <th align="left" class="blogcolumn">
                            Posts tagged ==%(tagname)s==
                  	      </th>
                    </tr>
                </thead>
            <tbody>""" % {'title':html_escape('asd'), "tagname":tagname})
        for feed in Feed.gql("WHERE taglist = :1 ORDER BY posts_month DESC",tagname):
            output.append("""
                 <tr>
                    <td valign="bottom" class="blogcolumn">
                       <a href="%(homepage)s">%(title)s</a>
                    </td>
                    <td valign="bottom" class="datecolumn">
                       %(weight_of_tag)s
                    </td>
                 </tr>""" % {'weight_of_tag': str(feed.taglist.count(tagname)), 'homepage': html_escape(feed.homepage), 'title': html_escape(feed.title) })
        output.append("""
              </tbody>
           </table> <br />
           <div id="tagcloud" style="width: 750px; height: 550px; position: relative;"></div> """)


        output.append( """ 
        <script type="text/javascript"> 
        /*!
       * Create an array of objects to be passed to jQCloud, each representing a word in the cloud and specifying
       * the following mandatory attributes:
       *
       * text: a string containing the word(s)
       * weight: a number (integer or float) defining the relative importance of the word
       *         (such as the number of occurrencies, etc.). The range of values is arbitrary, as they will
       *         be linearly mapped to a discrete scale from 1 to 10.
       *
       * You can also specify the following optional attributes:
       *

       * url: a URL to which the word will be linked. It will be used as the href attribute of an HTML anchor.
       * title: an HTML title for the span that will contain the word(s)
       */
       var word_list = [ """ )
        for tag_weight in weighted_taglist:
            if tag_weight[0] != "Uncategorized" and tag_weight[0] != "Uncategorized>" and tag_weight[0] != "Mathematics" and tag_weight[0] != "Math" and tag_weight[0] != "Maths" and tag_weight[0] != "Http://gdata.youtube.com/schemas/2007#video" and repr(tag_weight[0]) != repr(u'Matem\xe1ticas') and tag_weight[0] != "Matematica" and tag_weight[1]>10 :
               output.append(""" {text: "%(text)s", weight: %(weight)s, url: "/planettag2?content=%(text)s"}, """ % {"text":html_escape(tag_weight[0]), "weight": tag_weight[1] } )

        output.append( """
        ];
        window.onload = function() {
        // Call jQCloud on a jQuery object passing the word list as the first argument. Chainability of methods is maintained.
        $("#tagcloud").jQCloud(word_list);
        };
        </script>
            <div style="margin:20px;">

            <div id="cse-search-form" style="width: 100%;">
            Loading custom search. If you don't have JavaScript, you can use <a href="http://www.google.com/cse/home?cx=011837388000883284523:et7bffbfveg">this link</a> to search.
            </div>
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

        """ )
        return "".join(output)
