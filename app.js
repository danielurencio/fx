var express = require("express");
var app = express();
var engines = require("consolidate");
var MongoClient = require("mongodb").MongoClient;
var exec = require("child_process").exec;

app.engine("html", engines.nunjucks);
app.set("view engine", "html");
app.set("views", __dirname + "/views");
app.use(express.static(__dirname + '/'));


var command = "mongo --eval 'var año=2016,mes=5;' prueba.js --quiet";

MongoClient.connect("mongodb://localhost/fx", function(err, db) {

 app.get("/data", function(req,res) {

   exec(command, function(err,stdout) {
    var a = JSON.parse(stdout);
    res.json(a);
   });

 });

 app.get("/", function(req,res) {
  res.render("plot");
 });

});

app.listen(8080, 'localhost', function() {
 console.log("listening on 8080!");
});
