.PHONY: all clean-coverage clean-pyc clean-pyo runtests show-coverage

all: clean-coverage clean-pyc clean-pyo runtests show-coverage

clean-coverage:
	rm -f .coverage

clean-pyc:
	rm -f **/*.pyc *.pyc

clean-pyo:
	rm -f **/*.pyo *.pyo

runtests:
	coverage -x runtests.py

show-coverage:
	coverage -rm firmant/*.py firmant/**/*.py
