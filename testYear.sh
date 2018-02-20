while read -r line
  do
  python pg.py a $line
done < fechas.csv
