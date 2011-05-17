# This package is used to cut the string which is having html tags. 
# It does not count the html tags, it just count the string inside tags and keeps
# the tags as it is.

# ex: If the string is "welcome to <b>Python World</b> <br> Python is bla". and If we want to cut the string of 16 charaters then output will be "welcome to <b>Python</b>". 

# Here while cutting the string it keeps the tags for the cutting string and skip the rest and without distorbing the div structure.

# USAGE1:
#  obj = HtmlCutString("welcome to <b>Python World</b> <br> Python is",16)
#  newCutString = obj.cut()

# USAGE2:
#  newCutString = cutHtmlString("welcome to <b>Python World</b> <br> Python is",16)


from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString

class HtmlCutString():

    def __init__(self,string, limit):
        # temparary node to parse the html tags in the string
        self.tempDiv = parseString('<div>'+string+'</div>');
        # while parsing text no of characters parsed
        self.charCount = 0
        self.limit = limit


    def cut(self):
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, "some_tag", None)
        newDiv = newdoc.documentElement

        self.searchEnd(self.tempDiv, newDiv)
        # removeng some_tag that we added above
        newContent = newDiv.firstChild.toxml('utf-8')
        # removing div tag that we added in the __init__
        return newContent[5:-6]

    def deleteChildren(self,node):
        while node.firstChild:
            self.deleteChildren(node.firstChild)
            node.removeChild(node.firstChild)
             
  
    def searchEnd(self,parseDiv, newParent):
        for ele in parseDiv.childNodes:
            # not text node
            if ele.nodeType != 3:
                newEle = ele.cloneNode(True)
                newParent.appendChild(newEle)
                if len(ele.childNodes) == 0:
                    continue
                self.deleteChildren(newEle)
                res = self.searchEnd(ele,newEle)
                if res :
                    return res
                else:
                    continue;


            # the limit of the char count reached
            if (len(ele.nodeValue) + self.charCount) >= self.limit:
                newEle = ele.cloneNode(True)
                newEle.nodeValue = ele.nodeValue[0:(self.limit - self.charCount)]
                newParent.appendChild(newEle)
                return True

            newEle = ele.cloneNode(True)
            newParent.appendChild(newEle)
            self.charCount += len(ele.nodeValue)

        return False
    
def cutHtmlString(string, limit):
    output = HtmlCutString(string,limit)
    return output.cut()

