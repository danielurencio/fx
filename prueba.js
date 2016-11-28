var conn = new Mongo();
var db = conn.getDB("fx");

function Study(year,month) {
  this.year = year;
  this.month = month;
}

/////////////////////////////////////////////////////////////////////////////////
/////// FILTRAR
///////////////////////////////////////////////////////////////////////////////

Study.prototype.Filter = function(y,m,d) {

var array = [];

 for(var hrs=0; hrs<24; hrs++) {

  var secs = 59;
  var mins = 59;
  
  var a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs },{_id:0}).sort({ ms:-1 }).limit(1).toArray()[0];
    
  while(a == undefined && mins > 0) {
   secs--;
  if( secs < 0 ) { secs = 59; mins-- };
  if( mins < 58 ) break;  // <---- que tan rápido cortar el proceso..
 
   a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs },{_id:0}).sort({ ms:-1 }).limit(1).toArray()[0];
 
 }

  if( a != undefined ) array.push(a);
  
 }

 return array;
};

/////////////////////////////////////////////////////////////////////////////////
//////// OBTENER DÍAS ÚTILES
//////////////////////////////////////////////////////////////////////////////

Study.prototype.order = function() {
 var orden = db.order.find({ año: this.year, mes: this.month }).count();

 if( orden != 0 ) {
  var info = db.order.find({ año: this.year, mes:this.month }).toArray()[0];
  this.dias = info.dias;
  this.semanas = info.semanas;
 } else {
 var array = [];
// print("Calibrando..");

 for(var i=1; i<32; i++) {
  var day = this.Filter(this.year,this.month,i);
  array.push({ horas:day.length, dia:i });
//  print(day.length,i);
 }

var dias = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"];
var b = [];
var c = 0;

 for( var i in array) {
  if( array[i].horas == 0 ) {
   array[i].is = false;
   b.push(c);
   c++;

  if(array[i-1] && array[i-1].horas == 0) { c--; b.splice(b.length-1, 1); }

  } else {
   array[i].is = c;
//   delete array[i].horas;
  }

 }


 array = array.filter(function(d) { return !d.is == false; });

 array.forEach(function(d) {
  delete d.horas;
 });
 
 if( b[0] == 0 ) {
  b = b.map(function(d) { return d + 1; });
 }

 var obj = {};
 b.forEach(function(d) {
  obj[String(d)] = array.filter(function(e) { return e.is == d; });
 });
 
 obj.todos = array;

 this.dias = obj;
 this.semanas = b.length;

 db.order.insert({ año:this.year, mes:this.month, dias:this.dias, semanas:this.semanas});
 }
 //print("¡Listo!");
}

/////////////////////////////////////////////////////////////////////////////////
///////// GENERATE DATASET
///////////////////////////////////////////////////////////////////////////////

Study.prototype.DATA = function(k) {
 var b = [];
 var dias = this.dias[k].map(function(d) { return d.dia; });

  for(var i in dias) {
    if( i == 0 ) {
      b = this.Filter(this.year,this.month,dias[i]);
    } else {
      b = b.concat(this.Filter(this.year,this.month,dias[i]));
    }
  };

  this.data = b; //return b
}


//////////////////////////////////////////////////////////////////////////
/////// ADD SIMPLE MOVING AVERAGES TO DATASET
////////////////////////////////////////////////////////////////////////

Study.prototype.SMA = function(n) {

  var c = this.data.length - 1;

  while( c >= n ) {
    var arr = [];
    for(var i=0; i<n; i++) {
      arr.push( this.data[c-i].bid );
    }

    var ma = arr.reduce(function sum(a,b) { return a + b; }) / arr.length;
    this.data[c]["ma" + n] = ma;
    c--;
  }

// return b;
}


//////////////////////////////////////////////////////////////////////////////
/////  MA CROSSOVER
////////////////////////////////////////////////////////////////////////////

Study.prototype.CROSSOVER = function(a,b) {
 var largeMA, not, goForward = false;
 if(a > b) { largeMA=a;not=b; } else { largeMA=b;not=a; }
var check = this.data.filter(function(d) { return d["ma" + largeMA]; }).length;
 check != 0 ? doCross(largeMA,this.data):print("No such MA: " + largeMA);

 function doCross(largeMA,data) {
  var f = data.filter(function(d) { return d["ma" + largeMA]; });
  var checkAgain = data.filter(function(d) { return d["ma" + not]; }).length;
  checkAgain != 0 ? goForward=true : print("No such MA: " + not);
 }

 if(goForward) {
 //  print("ready to check crosses!");
  this.data = this.data.filter(function(d) { return d["ma" + largeMA]; });

  for(var i in this.data) {
   var upCondition = this.data[i].ma8 > this.data[i].ma24 && this.data[i-1]
                  && this.data[i-1].ma8 < this.data[i-1].ma24;

   var downCondition = this.data[i].ma8 < this.data[i].ma24 && this.data[i-1]
                    && this.data[i-1].ma8 > this.data[i-1].ma24;

      if( upCondition ) {
        this.data[i].dir = 1;
      } else if ( downCondition ) {
	this.data[i].dir = -1;
      }

   }

 }

}

var mayo2016 = new Study(año,mes);
mayo2016.order();
mayo2016.DATA("2");
mayo2016.SMA(8);
printjson(mayo2016.data);


/*
db.EURUSD.find({
 $or:[ 
  { year:2016, month:5, day:30, hour:{ $gte:12 } },
  { year:2016, month:5, day:31, hour:{ $lte:8 } }
 ]
}).sort({
 year:1,
 month:1,
 day:1,
 hour:1,
 minutes:1,
 seconds:1,
 ms:1
});
*/

