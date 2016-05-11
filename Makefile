PARITY=EURUSD
YEAR=2010
MONTH1=08
MONTH2=AUGUST

2: 1
	unzip file.zip
	rm file.zip
	cut -d , -f 1 ${PARITY}-${YEAR}-${MONTH1}.csv > parity.csv
	cut -d , -f 2 ${PARITY}-${YEAR}-${MONTH1}.csv > date.csv
	cut -d , -f 3,4 ${PARITY}-${YEAR}-${MONTH1}.csv > rest.csv
	cat date.csv | tr " " "," > date1.csv
	cat date1.csv | tr ":" "," > date2.csv
	cat date2.csv | tr "." "," > date3.csv
	paste -d , parity.csv date3.csv rest.csv > FILE.csv
	rm parity.csv date* rest.csv ${PARITY}-${YEAR}-${MONTH1}.csv
	perl -p -i -e 's/${YEAR}${MONTH1}/${YEAR},${MONTH1},/g' FILE.csv ## Éste comando  modifica línea por línea: 's/antes/después/g'
	echo "currency,year,month,day,hour,minutes,seconds,ms,bid,ask" > head.csv
	cat head.csv FILE.csv > file.csv
	rm FILE.csv head.csv
	touch 2
		

1:
	touch 1
	curl -o file.zip "http://truefx.com/dev/data/${YEAR}/${MONTH2}-${YEAR}/\
	${PARITY}-${YEAR}-${MONTH1}.zip"

mongoimport:
	mongoimport --file file.csv --type csv --headerline -d fx -c ${PARITY}

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
	rm 1 2 *.csv
