function hours(collection) {
    var newcollection = collection + "_h";

    return db.getCollection(collection).aggregate([
//        { $match: { year: 2010, month:1 } },
        { $project: {
	  _id:0,
	  year:1,
	  month:1,
	  hour:1,
	  minutes:1,
	  seconds:1,
	  ms:1,
	  day:1,
	  bid:1,
	  ask:1
	} },
        { $group: {
            _id: { year:"$year", month:"$month", day: "$day", hour: "$hour"},
            minutes: { $max: "$minutes" },
            seconds: { $first: "$seconds" },
            ms: { $first: "$ms" },
            bid: { $first: "$bid" },
            ask: { $first: "$ask" }
        } },
	{ $project: {
	    _id: 0,
	    year: "$_id.year",
	    month: "$_id.month",
	    day: "$_id.day",
	    hour: "$_id.hour",
	    bid: 1,
	    ask:1
	} },
        { $sort: { year:1, month:1, day:1 } },
        { $out: newcollection }
        ]);
}

function ma() {
  db.eurusd_h.aggregate([
     { $sort: { year:-1, month:-1, day:-1, hour:-1} },
     { $skip: 0 },
     { $limit: 8 },
     { $group: { _id:0, ma: { $avg: "$bid" } } }
  ]);
};
