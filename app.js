var fs = require("fs");
var d3 = require("d3");

fs.readFile("head.csv", "utf8", function (err, data) {
    if (err) {
	return console.error(err);
    }

//    console.log(data.toString()); // Esto cumple una función similar a "cat <file>"

    dato = d3.csv.parse(data, type);

    function type(d) {
	d.bid = +d.bid;
	d.ask = +d.ask;
	d.time = d3.time.format("%H:%M:%S.%L").parse(d.time);
	return d;
    }
    console.log(dato[0].time);
    console.log(dato[2].time.getMilliseconds());

    console.log(dato);

});


