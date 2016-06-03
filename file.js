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
