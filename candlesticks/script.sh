array=($(ls -f *.csv))

for i in ${!array[@]}; do
  python tick_to_candles.py ${array[$i]} ${i};
  cat data${i}.csv >> complete.csv;
done

cat header complete.csv > EURUSD15Min.csv;
