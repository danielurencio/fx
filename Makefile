eurusd-2015-01.csv: EURUSD-2015-01.zip
	unzip EURUSD-2015-01.zip
	rm EURUSD-2015-01.zip
	cut -d , -f 1 EURUSD-2015-01.csv > parity.csv
	cut -d , -f 2 EURUSD-2015-01.csv > date.csv
	cut -d , -f 3,4 EURUSD-2015-01.csv > rest.csv
	cat date.csv | tr " " "," > date1.csv
	cat date1.csv | tr ":" "," > date2.csv
	cat date2.csv | tr "." "," > date3.csv
	paste -d , parity.csv date3.csv rest.csv > Eurusd-2015-01.csv
	rm parity.csv date* rest.csv EURUSD-2015-01.csv
	perl -p -i -e 's/201501/2015,01,/g' Eurusd-2015-01.csv ## Éste comando  modifica línea por línea: 's/antes/después/g'
	echo "currency,year,month,day,hour,minutes,seconds,ms,bid,ask" > head.csv
	cat head.csv Eurusd-2015-01.csv > eurusd-2015-01.csv
	rm Eurusd-2015-01.csv head.csv
		

EURUSD-2015-01.zip:
	curl -o EURUSD-2015-01.zip "http://truefx.com/dev/data/2015/JANUARY-2015/EURUSD-2015-01.zip"


package.json:
	echo '{' > package.json
	echo '  "name": "forexbulb",' >> package.json
	echo '  "version": "0.0.0",' >> package.json
	echo '  "main": "app.js",'  >> package.json
	echo '  "author": "Daniel Urencio",' >> package.json
	echo '  "dependencies": {' >> package.json
	echo '    "d3": "~3.5.6"' >> package.json
	echo '  }' >> package.json
	echo '}' >> package.json
	npm install

clean:
	rm eurusd-2015-01.csv -r node_modules package.json
