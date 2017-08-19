array=($(ls -f *.csv))

for i in ${!array[@]}; do
  python file.py ${array[$i]} ${i};
  cat data${i}.csv >> complete.csv;
done

cat header complete.csv > EURUSD15Min.csv;
