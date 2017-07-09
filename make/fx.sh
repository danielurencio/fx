ordenar() {
# unzip $1;
 cat ${1} | tr " " "," | tr ":" "," | sed "s/\([0-9][0-9][0-9][0-9]\)\([0-9][0-9]\)\([0-9][0-9]\)/\1,\2,\3/g" | sed "s/\(,[0-9][0-9]\).\([0-9][0-9][0-9]\)/\1,\2/g" > ${1%.*}_r.csv
 echo "currency,year,month,day,hour,minutes,seconds,ms,bid,ask" > head.csv;
 cat head.csv ${1%.*}_r.csv > ${1%.*}_R.csv;
 rm head.csv ${1%.*}_r.csv;
 rm $1; mv ${1%.*}_R.csv $1
}

data() {
 YEAR=${1}
 MONTH1=${2}
 PARITY=${3}
 if [[ ${#MONTH1} == 1 ]]; then
  MONTH1=0$MONTH1
 fi

 if [[ $MONTH1 == 01 ]]; then
  MONTH2=JANUARY
 elif [[ $MONTH1 == 02 ]]; then
  MONTH2=FEBRUARY
 elif [[ $MONTH1 == 03 ]]; then
  MONTH2=MARCH
 elif [[ $MONTH1 == 04 ]]; then
  MONTH2=APRIL
 elif [[ $MONTH1 == 05 ]]; then
  MONTH2=MAY
 elif [[ $MONTH1 == 06 ]]; then
  MONTH2=JUNE
 elif [[ $MONTH1 == 07 ]]; then
  MONTH2=JULY
 elif [[ $MONTH1 == 08 ]]; then
  MONTH2=AUGUST
 elif [[ $MONTH1 == 09 ]]; then
  MONTH2=SEPTEMBER
 elif [[ $MONTH1 == 10 ]]; then
  MONTH2=OCTOBER
 elif [[ $MONTH1 == 11 ]]; then
  MONTH2=NOVEMBER
 elif [[ $MONTH1 == 12 ]]; then
  MONTH2=DECEMBER
 fi

 MONTH3=$(echo $MONTH2 | tr A-Z a-z);

 if [[ ${YEAR} > 2016 && ${MONTH1} > 03 ]]; then
    curl "http://truefx.com/dev/data/${YEAR}/${YEAR}-${MONTH1}/${PARITY}-${YEAR}-${MONTH1}.zip" -H "Referer: http://truefx.com/?page=download&description=${MONTH3}${YEAR}&dir=${YEAR}/${YEAR}-${MONTH1}" > ${YEAR}-${MONTH1}.zip
 else
curl "http://www.truefx.com/dev/data/${YEAR}/${MONTH2}-${YEAR}/${PARITY}-${YEAR}-${MONTH1}.zip" -H "Referer: http://www.truefx.com/?page=download&description=${MONTH3}${YEAR}&dir=${YEAR}/${MONTH2}-${YEAR}" > ${YEAR}_${MONTH1}.zip
 fi

}

TODO() {
 for m in 5 6 7 8 9 10 11 12; do
  data 2009 $m EURUSD
  unzip *.zip; rm *.zip
  data *.csv
  mongoimport -d fx -c EURUSD --headerline --type=csv *.csv
  rm *.csv
 done

 for y in 2010 2011 2012 2013 2014 2015 2016; do
  for m in 1 2 3 4 5 6 7 8 9 10 11 12; do
   data $y $m EURUSD
   unzip *.zip; rm *.zip
   data *.csv
   mongoimport -d fx -c EURUSD --headerline --type=csv *.csv
   rm *.csv  
  done
 done

 for m in 1 2 3 4 5 6; do
  data 2017 $m EURUSD
  unzip *.zip; rm *.zip
  data *.csv
  mongoimport -d fx -c EURUSD --headerline --type=csv *.csv
  rm *.csv
 done

}
