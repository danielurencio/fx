MONTHS=(JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER)
YEARS=(2009 2010 2011 2012 2013 2014 2015 2016)
c=0
CURRENCY=EURUSD

for e in ${YEARS[@]}
    do
	for i in ${!MONTHS[@]}
	    do a=`expr ${i} + 1`; 
	    if [ `expr length ${a}` = 1 ]; then
		make PARITY=$CURRENCY MONTH1=${c}${a} MONTH2=${MONTHS[$i]} YEAR=$e
		make mongoimport PARITY=$CURRENCY
		make clean
	#	mongo file.js
	    else 
		make PARITY=$CURRENCY MONTH1=${a} MONTH2=${MONTHS[$i]} YEAR=$e
		make mongoimport PARITY=$CURRENCY
		make clean
	#	mongo file.js
	    fi
	done
done
