var exec = require("child_process").exec;
var command = "mongo --eval 'var año=2016,mes=5;' prueba.js --quiet";

exec(command, function(err,stdout) {
 var a = JSON.parse(stdout);
 console.log(a);
});
