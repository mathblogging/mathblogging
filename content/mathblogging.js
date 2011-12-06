var load_page, post_to_row, process_json;

process_json = function(data) {
  var row;
  return "<table id='posts' class='tablesorter'><thead><tr><th>Date</th><th>Blog</th><th>Post</th><th>Category</th><th>Tags</th><th>#Comments</th></tr></thead><tbody>" + (((function() {
    var _i, _len, _ref, _results;
    _ref = data.posts;
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      row = _ref[_i];
      _results.push(post_to_row(row));
    }
    return _results;
  })()).join("")) + "</tbody></table>";
};

post_to_row = function(post) {
  return "<tr>   <td>" + post.date + "</td>   <td>" + post.blog + "</td>   <td>" + post.title + "</td>   <td>" + post.category + "</td>   <td>" + (post.tags.join(", ")) + "</td>   <td>" + post.comments + "</td>   </tr>";
};

load_page = function() {
  return $.getJSON("http://staging.mathblogging.org/json", function(data) {
    $('#content').append(process_json(data));
    return $("#posts").tablesorter({
      sortList: [[0, 0], [0, 1]],
      widgets: ["zebra"]
    });
  });
};