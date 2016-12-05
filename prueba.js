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


Study.prototype.FilterMins = function(y,m,d,n) {

var array = [];

 for(var hrs=0; hrs<24; hrs++) {

//  var secs = 59;
//  var mins = 59;
  var c = 1;

  for(var mins=-1; mins<=59; mins+=n) {
   var secs = 59;

   if(mins!=-1) {
      var a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs },{_id:0}).sort({ ms:-1 }).limit(1).toArray()[0];
       
//      print( (n-2)*c );

      while(a == undefined ) {//&& mins < (n-2)*c ) {
       secs--;
      if( secs < 0 ) { secs = 59; mins--;};
      if( mins < (n-2)*c ) {  break; } // <---- que tan rápido cortar el proceso..
 
       a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs },{_id:0}).sort({ ms:-1 }).limit(1).toArray()[0];

     }

     c++
    if( a != undefined ) array.push(a);
  }

  }
//print("Son las " + hrs + "--------------");
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

Study.prototype.DATA = function(k,interval) {
 var b = [];
 var dias = this.dias[k].map(function(d) { return d.dia; });

  for(var i in dias) {
    if( i == 0 ) {
      b = this.FilterMins(this.year,this.month,dias[i],interval);
    } else {
      b = b.concat( this.FilterMins(this.year,this.month,dias[i],interval) );
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

Study.prototype.WMA = function(n) {

  var c = this.data.length - 1;

  while( c >= n ) {
    var arr = [];
    for(var i=0; i<n; i++) {
      arr.push({ val:this.data[c-i].bid, weight:i+1 });
    }

    var triangularSum = arr.map(function(d) { return d.weight; }).reduce(function sum(a,b) { return a + b; });

//    var ma = arr.reduce(function sum(a,b) { return a + b; }) / arr.length;
    arr.forEach(function(d) { d.wVal = d.val * ( d.weight / triangularSum ); });

    var wma = arr.map(function(d) { return d.wVal; }).reduce(function sum(a,b) { return a + b; });

    this.data[c]["wma" + n] = wma;
    c--;
  }

}

//////////////////////////////////////////////////////////////////////////////
/////  MA CROSSOVER
////////////////////////////////////////////////////////////////////////////

Study.prototype.CROSSOVER = function(a,b) {
 var largeMA, smallMA, goForward = false;
 if(a > b) { largeMA=a;smallMA=b; } else { largeMA=b;smallMA=a; }
var check = this.data.filter(function(d) { return d["ma" + largeMA]; }).length;
 check != 0 ? doCross(largeMA,this.data):print("No such MA: " + largeMA);

 function doCross(largeMA,data) {
  var f = data.filter(function(d) { return d["ma" + largeMA]; });
  var checkAgain = data.filter(function(d) { return d["ma" + smallMA]; }).length;
  checkAgain != 0 ? goForward=true : print("No such MA: " + smallMA);
 }

 if(goForward) {
 //  print("ready to check crosses!");
  this.data = this.data.filter(function(d) { return d["ma" + largeMA]; });

  for(var i in this.data) {
   var upCondition=this.data[i]["ma" + smallMA] > this.data[i]["ma" + largeMA] && this.data[i-1]
                  && this.data[i-1]["ma" + smallMA] < this.data[i-1]["ma" + largeMA];

   var downCondition=this.data[i]["ma" + smallMA] < this.data[i]["ma"+ largeMA] && this.data[i-1]
                    && this.data[i-1]["ma"+smallMA] > this.data[i-1]["ma"+largeMA];

      if( upCondition ) {
        this.data[i].dir = 1;
      } else if ( downCondition ) {
	this.data[i].dir = -1;
      }

   }

 }

}


Study.prototype.CrossAnalysis = function() {
  var crosses = this.data.filter(function(d) { return d.dir; });
  if( crosses.length == 0 ) return;

//  print(crosses.length);

  for(var i=1; i<crosses.length; i++) {
   crosses[i].dir > 0 ? UP() : DOWN();
  };

  function UP() {
    var result = crosses[i].ask - crosses[i-1].bid;
    print( result, periods(crosses[i-1],crosses[i]) );
  }

  function DOWN() {
    var result = crosses[i-1].ask - crosses[i].bid;
    print( result, periods(crosses[i-1],crosses[i]) );
  }

  function periods(a,b) {
    if(a.day != b.day ) var p = 24 - a.hour + b.hour;
    else { var p = b.hour - a.hour; }
    return p;
  }

};
/*
var mayo2016 = new Study(año,mes);
mayo2016.order();
mayo2016.DATA("1",15);
mayo2016.SMA(8);
mayo2016.WMA(8);
printjson(mayo2016.data);
*/

//load("prueba.js"); var mayo2016 = new Study(2016,5); mayo2016.order();mayo2016.DATA("1",60); mayo2016.SMA(8); mayo2016.SMA(24); mayo2016.CROSSOVER(8,24);

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

