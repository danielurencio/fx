MONTHS=(JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER)

for i in ${!MONTHS[@]}
    do make PARITY=GBPUSD MONTH1=`expr $i + 1` MONTH2=${MONTHS[$i]} YEAR=2010 #echo `expr $i + 1` ${MONTHS[$i]}
       make mongoimport PARITY=GBPUSD
       make clean
done
