//function wma() {
var l = db.eurusd_h.find().count();

//for(var i = 0; i<l; i++) {
var a = db.eurusd_h.aggregate([
{ $sort: { year:-1, month:-1, day:-1, hour:-1 } },
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

function ma(n) {
  for(var i=0; i<docss.length; i++) {
    var ma = [];
//    ma.push(docs[i].bid,docs[i+1].bid,docs[i+2].bid,docs[i+3].bid,docs[i+4].bid);
    for(var j=0; j<n; j++) {
	ma.push( docss[i+j].bid );
    };

    var result = ma.reduce(function sum(a,b) { return a + b; }, 0);
    result = result/n;

    var name = "ma" + n;
    docss[i][name] = result;
  }
}
