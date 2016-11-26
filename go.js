var MongoClient = require("mongodb").MongoClient;

var array = [];

MongoClient.connect("mongodb://localhost:27017/fx", function(err,db) {

 db.collection("EURUSD", function(err,col) {

  for(var i=1; i<32; i++) {
    for(var j=0; j<24; j++) {

	  col.find({
	  'year': 2016,
	  'month':5,
	  'day':i,
	  'hour':j,
	  'minutes':59,
	  'seconds':59
	  })
	  .sort({ 'ms':-1 })
	  .limit(1)
	  .forEach(function(doc) { 
	    array.push(doc);
	     console.log(Object.keys(doc).length);
//	     console.log(array.length);
	  });

    }
   }

 });


});
