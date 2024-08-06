all:
# csvファイルは手で修正しているので、うかつに上書きしないように。
	# ls 2???.pdf | sed -e s/pdf/csv/ | xargs make
	python combine.py

%.csv: %.pdf # pdf2csv.py
	python pdf2csv.py $* 

%_P.csv: %.pdf # pdf2csv.py
	python pdf2csv_P.py $* 
