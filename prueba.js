var conn = new Mongo();
var db = conn.getDB("fx");

function Study(year,month,day) {
  this.year = year;
  this.month = month;
  this.day = day;
}


function filter(y,m,d) {

var array = [];

 for(var j=0; j<24; j++) {

  var secs = 59;
  var a = db.EURUSD.find({ year:y, month:m, day:d, hour:j, minutes:59, seconds:secs }).sort({ ms:-1 }).limit(1).toArray()[0];

  while(a == undefined) {
   secs--;
  if(secs<0) break;

   a = db.EURUSD.find({ year:y, month:m, day:d, hour:j, minutes:59, seconds:secs }).sort({ ms:-1 }).limit(1).toArray()[0];


 }

  if( a != undefined ) array.push(a);

 }

 return array;
}

////////////////////////////
Study.prototype.filter = function(y,m,d) {

var array = [];

 for(var hrs=0; hrs<24; hrs++) {

  var secs = 59;
  var mins = 59;
  
  var a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs }).sort({ ms:-1 }).limit(1).toArray()[0];
    
  while(a == undefined && mins > 0) {
   secs--;
  if( secs < 0 ) { secs = 59; mins-- };
  if( mins < 58 ) break;  // <---- que tan rápido cortar el proceso..
 
   a = db.EURUSD.find({ year:y, month:m, day:d, hour:hrs, minutes:mins, seconds:secs }).sort({ ms:-1 }).limit(1).toArray()[0];
 
 }

  if( a != undefined ) array.push(a);
  
 }

 return array;
};


Study.prototype.order = function(month,year) {
 var array = [];
 for(var i=1; i<32; i++) {
  var day = this.filter(year,month,i);
  array.push({ horas:day.length, dia:i });
  print(day.length,i);
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
 
 var obj = {};
 b.forEach(function(d) {
  obj[String(d)] = array.filter(function(e) { return e.is == d; });
 });
 
 obj.todos = array;
 print(b);

 return obj;
}


Study.prototype.hola = function() { print("hola"); }
