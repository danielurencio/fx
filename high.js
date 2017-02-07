var MongoClient = require("mongodb").MongoClient;
var año = process.argv[2];
var mes = process.argv[3];
var query = { 'year':Number(año), 'month':Number(mes) };
var A = [];

MongoClient.connect("mongodb://localhost:27017/fx", function(err,db) {
  var stream = db.collection("EURUSD").find(query).stream();
  var mins = 0, secs = 0, arr = ['',''];
  var steps = [15,30,45,0], c = 0;
  var high = 0;
//  var steps = [5,10,15,20,25,35,40,45,50,55,0];

  stream.on("data", function(doc) {

    if( doc.minutes == steps[c] ) {
      c > steps.length - 1 ? c = 0 : 0;
      if( doc.ask > high ) high = doc.ask;
    }

  });

});
