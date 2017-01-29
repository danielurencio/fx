var MongoClient = require("mongodb").MongoClient;

MongoClient.connect("mongodb://localhost:27017/fx", function(err,db) {
  var stream = db.collection("EURUSD").find().stream();
  stream.on("data", function(docs) {
    console.log(docs);
  });
});
