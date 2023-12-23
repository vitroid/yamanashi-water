all:
	ls 2???.pdf | sed -e s/pdf/pickle/ | xargs make
	python stack.py

%.pickle: %.pdf scan.py
	python scan.py $* 

