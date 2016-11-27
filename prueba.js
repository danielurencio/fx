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

  return b;
}


//////////////////////////////////////////////////////////////////////////
/////// ADD SIMPLE MOVING AVERAGES TO DATASET
////////////////////////////////////////////////////////////////////////

Study.prototype.SMA = function(data,n) {

  var c = data.length - 1;

  while( c >= n ) {
    var arr = [];
    for(var i=0; i<n; i++) {
      arr.push( data[c-i].bid );
    }

    var ma = arr.reduce(function sum(a,b) { return a + b; }) / arr.length;
    data[c]["ma" + n] = ma;
    c--;
  }

// return b;
}


//////////////////////////////////////////////////////////////////////////////
/////  MA CROSSOVER
////////////////////////////////////////////////////////////////////////////

Study.prototype.CROSSOVER = function(a,b) {
 
}
/*
var mayo2016 = new Study(año,mes);
mayo2016.order();
var data = mayo2016.DATA("1");
printjson(data);
*/
