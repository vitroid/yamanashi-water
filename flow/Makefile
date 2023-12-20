all:
	ls 2???.pdf | sed -e s/pdf/pickle/ | xargs make


%.pickle: %.pdf
	python scan.py $* 

