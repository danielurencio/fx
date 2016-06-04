var conn = new Mongo();
db = conn.getDB("fx");

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

function date(collection) {
    var ids = [], docs = [];

    //return
     db.getCollection(collection).find({}).forEach(
	function(d) {
	  var a = d;
//	  var id = a._id;
	  a.date = new Date(a.year,a.month-1,a.day,a.hour,a.minutes,a.seconds,a.ms);
	  a.weekday = a.date.getDay();
	  //ids.push(id); 
	  docs.push(a);
	
//    print(array[array.length-1]);
    });
    print(docs.length);

    db.getCollection(collection).drop();

    var bulk = db.AUDUSD.initializeUnorderedBulkOp();
    
    for(var i=0; i<docs.length; i++) {
	bulk.insert(docs[i]);
    }

    bulk.execute();

    print("Done!");

}
