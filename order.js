var conn = new Mongo();
var db = conn.getDB("fx");
//var a = db.EURUSD.find().limit(1).toArray();
//print(a[0].ask);
var a = db.getCollection("eurusd_" + year + "_" + month).find().sort({ 'day':1, 'hour':1, 'minutes':1 }).toArray();
db.getCollection("eurusd_" + year + "_" + month).drop();
db.getCollection("eurusd_" + year + "_" + month).insert(a);
