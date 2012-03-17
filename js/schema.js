var schema = {
    "/type/tag": {
        "type": "/type/type",
        "name": "Tag",
        "properties": {
            "name": {"name": "Name", "unique": true, "type": "string", "required": true},
            "blogs": {"name": "Blogs", "unique": false, "type": "/type/blog", "required": false},
            "posts": {"name": "Posts", "unique": false, "type": "/type/post", "required": false}
        }
    },
    "/type/blog": {
        "type": "/type/type",
        "name": "Blog",
        "properties": {
            "name": {"name": "Name", "unique": true, "type": "string", "required": true},
            "url": {"name": "Homepage", "unique": true, "type": "string", "required": true},
            "posts": {"name": "Posts", "unique": false, "type": "/type/post", "required": false},
            "category": {"name": "Category", "unique": true, "type": "string", "required": false},
            "tags": {"name": "Tags", "unique": false, "type": "/type/tag", "required": false},
            "language": {"name": "Language", "unique": true, "type": "string", "required": false},
            "comments-day": {"name": "Comments per Day", "unique": true, "type": "integer", "required": false},
            "comments-week": {"name": "Comments per Week", "unique": true, "type": "integer", "required": false},
            "posts-week": {"name": "Posts per Week", "unique": true, "type": "integer", "required": false},
            "posts-month": {"name": "Posts per Month", "unique": true, "type": "integer", "required": false}
        }
    },
    "/type/post": {
        "type": "/type/type",
        "name": "Post",
        "properties": {
            "title": {"name": "Title", "unique": true, "type": "string", "required": true},
            "url": {"name": "URL", "unique": true, "type": "string", "required": true},
            "blog": {"name": "Blog", "unique": true, "type": "/type/blog", "required": true},
            "date": {"name": "Date", "unique": true, "type": "string", "required": false},
            "tags": {"name": "Tags", "unique": false, "type": "/type/tag", "required": false},
            "length": {"name": "Length", "unique": true, "type": "integer", "required": false}
        }
    }
}
