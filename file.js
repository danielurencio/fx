var conn = new Mongo();
db = conn.getDB("fx");
/*
function a(collection) {
    return db.getCollection(collection).aggregate([
	{ $match: { year: 2010, month:1 } },
	{ $project: { _id:0, hour:1, minutes:1, seconds:1, ms:1, day:1, bid:1, ask:1 } },
	{ $group: {
	    _id: {  day: "$day", hour: "$hour"},
	    minutes: { $max: "$minutes" },
	    seconds: { $first: "$seconds" },
	    ms: { $first: "$ms" },
	    bid: { $first: "$bid" },
	    ask: { $first: "$ask" }
	} },
	{ $sort: { "_id.day":1, "_id.hour":1 } },
	{ $out: "eurusd_hourly" }
	]);
}
*/
function date(collection,y,m) {
  var start = Date();
  var docs = [];
  print(collection, y, m);

  for(var d=1; d<32; d++) {
  
    print(Date() + " Pushing documens: " + y + "/" + m + "/" + d);

     db.getCollection(collection).find({year:y,month:m,day:d}).forEach(
	function(d) {
	  var a = d;
	  a.date = new Date(a.year,a.month-1,a.day,a.hour-5,a.minutes,a.seconds,a.ms);
	  a.weekday = a.date.getDay();
	  docs.push(a);
        });

//    print(docs.length);

//    db.getCollection(collection).drop();

    var smallcaps = collection.toLowerCase();
    var bulk = db.getCollection(smallcaps).initializeUnorderedBulkOp();
    print(Date() + " Adding documents to 'bulk'.");
    
    for(var i=0; i<docs.length; i++) {
	bulk.insert(docs[i]);
    }

    print(Date() + " Executing 'bulk' now.");
    bulk.execute();

    print(Date() + " Done!");
    print(docs.length);
    docs = [];
  }

  var end = Date();

  print("Started at: " + start);
  print("Ended at: " + end);
}
