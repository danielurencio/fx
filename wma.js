<<<<<<< HEAD
function wma() {
var l = db.eurusd_h.find().count();
=======
function Study(db,collection) {
  var connection = new Mongo().getDB(db);
  this.c = connection.getCollection(collection);
};
>>>>>>> 4ed993ae789ced76494030ffc239a97a41b49cbe

Study.prototype.count = function() {
  print(this.c.find().count());
};

Study.prototype.wma = function(n) {
  var l = this.c.find().count();
  print("Going through " + l + " documents.");
  var bulk = this.c.initializeUnorderedBulkOp();
  print("Initilized unordered bulk operation.");

  var conteiner = [];

  for(var j = 0; j<l; j++) {

    var a = this.c.aggregate([
      { $sort: { year:-1, month:-1, day:-1, hour:-1 } },
      { $skip:j },
      { $limit: n }
    ]).toArray();

    for(var i in a) { a[i].n = a.length - i; };

    var triangularSum = a.map(function(d) { return d.n; })
     .reduce(function sum(a,b) { return a + b; },0);

<<<<<<< HEAD
=======
    var b = [];

    for(var i in a) { b.push( a[i].bid * ( a[i].n / triangularSum ) ); };

    var result = b.reduce(function sum(a,b) { return a + b; }, 0);

 //   conteiner.push({ _id:a[0]._id, wma: result });
    bulk.find({ _id:a[0]._id }).update({ $set: { "wma": result } });

    print("Added document " + j + " to bulk.");

  };

/*  for(var i in conteiner) {
    bulk.find({ _id:conteiner[i]._id })
	.udpate({ $set: { wma: conteiner[i] } });
  };
*/
  print("Executin the whole bulk now.");
  bulk.execute();
>>>>>>> 4ed993ae789ced76494030ffc239a97a41b49cbe
}

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
