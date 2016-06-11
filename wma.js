//function wma() {
var l = db.eurusd_h.find().count();

//for(var i = 0; i<l; i++) {
var a = db.eurusd_h.aggregate([
{ $sort: { year:-1, month:-1, day:-1 } },
{ $skip:i },
{ $limit: 8 }
]).toArray()

for(var i in a) { a[i].n = a.length - i; };

var c= a.map(function(d) { return d.n; }).reduce(function sum(a,b) { return a + b; },0);

var b = [];

for(var i in a) { b.push( a[i].bid * ( a[i].n / c ) ); };

var result = b.reduce(function sum(a,b) { return a + b; }, 0);

db.eurusd_h.update({ _id:a[0]._id },{ $set: { wma: result } });
//}

//}
