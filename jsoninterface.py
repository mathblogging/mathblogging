from main import *
from django.utils import simplejson

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
            "tags": [ tag.name for tag in Tag.gql("WHERE blogs = :1", blog.key().id_or_name()) ],
            "language": blog.language,
            "comments_day": blog.comments_day,
            "comments_week": blog.comments_week,
            "posts_week": blog.posts_week,
            "posts_month": blog. posts_month
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
