MONTHS=(JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER)
c=0

for i in ${!MONTHS[@]}
    do a=`expr ${i} + 1`; 
    if [ `expr length ${a}` = 1 ]; then
	make PARITY=GBPUSD MONTH1=${c}${a} MONTH2=${MONTHS[$i]} YEAR=2010
	make mongoimport PARITY=GBPUSD
	make clean
    else 
	make PARITY=GBPUSD MONTH1=${a} MONTH2=${MONTHS[$i]} YEAR=2010
        make mongoimport PARITY=GBPUSD
        make clean
    fi
done
