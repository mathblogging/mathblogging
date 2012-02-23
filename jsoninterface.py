from main import *
from django.utils import simplejson
from copy import deepcopy

def posts_json():
    posts = {}
    for post in Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
        id = post.key().id_or_name()
        posts[id] = {
            "id": id,
            "title": post.title,
            "url": post.link,
            "blog": Feed.gql("WHERE title = :1", post.service).get().key().id_or_name(),
            "date": post.timestamp_created.strftime('%B %d,%Y %I:%M:%S %p'),
            "tags": [ Tag.gql("WHERE name = :1", tag).get().key().id_or_name() for tag in post.tags ], # TODO: access Tag by key of post!
            "length": post.length,
        }
    return posts
    
def blogs_json():
    blogs = {}
    for blog in Feed.gql("WHERE category IN :1", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
        id = blog.key().id_or_name()
        blogs[id] = {
            "id": id,
            "name": blog.title,
            "url": blog.homepage,
            "posts": [ post.key().id_or_name() for post in Post.gql("WHERE service = :1 ORDER BY timestamp_created DESC LIMIT 10", blog.title)],
            "tags": [ tag.key().id_or_name() for tag in Tag.gql("WHERE blogs = :1", blog.key().id_or_name()) ],
            "language": blog.language,
            "comments_day": blog.comments_day,
            "comments_week": blog.comments_week,
            "posts_week": blog.posts_week,
            "posts_month": blog.posts_month
        }
    return blogs

def tags_json():
    tags = {}
    for tag in Tag.all():
        id = tag.key().id_or_name()
        tags[id] = {
            "id": id,
            "name": tag.name,
            "blogs": tag.blogs,
            "posts": tag.posts
        }
    return tags
    
class TheJSONPHandler(CachedPage):
    mimeType = "application/javascript"
    def post_process_content(self, content):
        callback = self.request.get("callback")
        logging.info("Add JSONP padding: " + callback)
        return "%s(%s);" % (callback, content)
        
class PostsJSONP(TheJSONPHandler):
    cacheName = "PostsJSONP"
    def generatePage(self):
        output = posts_json()
        return simplejson.dumps(output)
        
class TagsJSONP(TheJSONPHandler):
    cacheName = "TagsJSONP"
    def generatePage(self):
        output = tags_json()
        return simplejson.dumps(output)

class BlogsJSONP(TheJSONPHandler):
    cacheName = "BlogsJSONP"
    def generatePage(self):
        output = blogs_json()
        return simplejson.dumps(output)

class DataJSONP(TheJSONPHandler):
    cacheName = "DataJSONP"
    def generatePage(self):
        output = {
            "blogs": blogs_json(),
            "posts": posts_json(),
            "tags": tags_json()
        }
        return simplejson.dumps(output)


################################
# Here begins the Data.js part #
################################

# Note: the syntax for JSON objects in Python and JavaScript is almost
# verbatim the same. The one difference in the snippet below is that
# in Python, the constants True and False have to be capitalized.

# The "Schema" is, if you will, a formal type definition for our JSON
# data structure.

datajs_schema = {
    "/type/tag": {
        "type": "/type/type",
        "name": "Tag",
        "properties": {
            "name": {"name": "Name", "unique": True, "type": "string", "required": True},
            "blogs": {"name": "Blogs", "unique": False, "type": "/type/blog", "required": False},
            "posts": {"name": "Posts", "unique": False, "type": "/type/post", "required": False}
        }
    },
    "/type/blog": {
        "type": "/type/type",
        "name": "Blog",
        "properties": {
            "name": {"name": "Name", "unique": True, "type": "string", "required": True},
            "url": {"name": "Homepage", "unique": True, "type": "string", "required": True},
            "posts": {"name": "Posts", "unique": False, "type": "/type/post", "required": False},
            "category": {"name": "Category", "unique": True, "type": "string", "required": False},
            "tags": {"name": "Tags", "unique": False, "type": "/type/tag", "required": False},
            "language": {"name": "Language", "unique": True, "type": "string", "required": False},
            "comments-day": {"name": "Comments per Day", "unique": True, "type": "integer", "required": False},
            "comments-week": {"name": "Comments per Week", "unique": True, "type": "integer", "required": False},
            "posts-week": {"name": "Posts per Week", "unique": True, "type": "integer", "required": False},
            "posts-month": {"name": "Posts per Month", "unique": True, "type": "integer", "required": False}
        }
    },
    "/type/post": {
        "type": "/type/type",
        "name": "Post",
        "properties": {
            "title": {"name": "Title", "unique": True, "type": "string", "required": True},
            "url": {"name": "URL", "unique": True, "type": "string", "required": True},
            "blog": {"name": "Blog", "unique": True, "type": "/type/blog", "required": True},
            "date": {"name": "Date", "unique": True, "type": "string", "required": False},
            "tags": {"name": "Tags", "unique": False, "type": "/type/tag", "required": False},
            "length": {"name": "Length", "unique": True, "type": "integer", "required": False}
        }
    }
}

# The procedure for generating the Data.js JSON object is basically
# the same as for the standard JSON object. The crucial differences
# are:
# 1) Objects of all three types are dumped into the same map called
# output.
# 2) References have to be prefixed with the type of the referenced
# object, i.e. "/post/<id>" instead of just "<id>".

class DataJS(TheJSONPHandler):
    cacheName = "DataJS"
    def generatePage(self):
        output = deepcopy(datajs_schema)
        # add blogs
        for blog in Feed.gql("WHERE category IN :1", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
            id = blog.key().id_or_name()
            output["/blog/"+id] = {
                "type": "/type/blog",
                "name": blog.title,
                "url": blog.homepage,
                "posts": [ "/post/" + post.key().id_or_name() for post in Post.gql("WHERE service = :1 ORDER BY timestamp_created DESC LIMIT 10", blog.title)],
                "category": blog.category,
                "tags": [ "/tag/" + tag.key().id_or_name() for tag in Tag.gql("WHERE blogs = :1", blog.key().id_or_name()) ],
                "language": blog.language,
                "comments-day": blog.comments_day,
                "comments-week": blog.comments_week,
                "posts-week": blog.posts_week,
                "posts-month": blog.posts_month 
            }
        # add posts
        for post in Post.gql("WHERE category IN :1 ORDER BY timestamp_created DESC LIMIT 150", ['history','fun','general','commercial','art','visual','pure','applied','teacher','journalism']):
            id = post.key().id_or_name()
            output["/post/"+id] = {
                "type": "/type/post",
                "title": post.title,
                "url": post.link,
                "blog": "/blog/" + Feed.gql("WHERE title = :1", post.service).get().key().id_or_name(),
                "date": post.timestamp_created.strftime('%B %d,%Y %I:%M:%S %p'),
                "tags": ["/tag/" + Tag.gql("WHERE name = :1", tag).get().key().id_or_name() for tag in post.tags ], # TODO: access Tag by key of post!,
                "length": post.length
            }            
        # add tags
        for tag in Tag.all():
            id = tag.key().id_or_name()
            output["/tag/"+id] = {
                "type": "/type/tag",
                "name": tag.name,
                "blogs": [ "/blog/" + blogid for blogid in tag.blogs],
                "posts": [ "/post/" + postid for postid in tag.posts]
            }
        # TODO cleanup broken links (maybe Data.js handles them gracefully?)
        return simplejson.dumps(output)

