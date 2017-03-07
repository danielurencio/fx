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

 curl "http://www.truefx.com/dev/data/${YEAR}/${MONTH2}-${YEAR}/${PARITY}-${YEAR}-${MONTH1}.zip" -H "Referer: http://www.truefx.com/?page=download&description=${MONTH3}${YEAR}&dir=${YEAR}/${MONTH2}-${YEAR}" > ${YEAR}_${MONTH1}.zip
 
# echo "http://www.truefx.com/dev/data/${YEAR}/${MONTH2}-${YEAR}/${PARITY}-${YEAR}-${MONTH1}.zip" -H "Referer: http://www.truefx.com/?page=download&description=${MONTH3}${YEAR}&dir=${YEAR}/${MONTH2}-${YEAR}";


}
