var MongoClient = require("mongodb").MongoClient;
var express = require("express");
var engines = require("consolidate");
var app = express();
var httpServer = require("http").createServer(app);

app.engine("html", engines.nunjucks);
app.set("view engine", "html");
app.set("views", __dirname + "/views");
app.use(express.static(__dirname + "/"));


MongoClient.connect("mongodb://localhost:27017/fx", function(err, db) {

  if(err) console.log(err);

  var query = db.collection("eurusd_h")
    .find({"year":2016,"month":4,"day":28})
    .sort({"hour":-1})
    .project({"_id":0});

  var stream = query.stream();

  query.on("error", function(err) {
    console.log(err);
  });

  stream.on("data", function(data) {
//    console.log(data);
  });

  app.get("/", function(req,res) {
    res.render("chart");
  });

  app.get("/data", function(req,res) {

    query.forEach(
      function(d) {
        array.push(d);
      },
      function() {
	res.json(array);
      });

    var array = [];
  });

});

var server = httpServer.listen("8080", function() {
    console.log("8080");
});
