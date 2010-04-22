# You can set these variables from the command line.
SPHINXOPTS    = -aE
SPHINXBUILD   = sphinx-build
SPHINXAUTOGEN = sphinx-autogen
PAPER         =
SOURCEDIR     = doc
BUILDDIR      = doc/_build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -W -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS)

.PHONY: test clean autogen html latex linkcheck doctest commithook

test: clean
	coverage -x ./runtests.py
	coverage -rm `find ./firmant -type f -iname '*.py'`

pylint:
	pylint --rcfile=pylintrc firmant

clean:
	-rm -rf $(BUILDDIR)/*
	-rm -rf $(SOURCEDIR)/generated/*
	-rm -rf `find ./ -type f -iname '*.pyc' -o -iname '*.pyo'`
	-rm -rf .coverage

autogen:
	env PYTHONPATH=. $(SPHINXAUTOGEN) -o doc/generated doc/modules.rst

html: autogen
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

latex: autogen
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

linkcheck: autogen
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

commithook:
	make clean
	make test
	make pylint
	make html -e SPHINXOPTS='-aE -W -Q'
	make latex -e SPHINXOPTS='-aE -W -Q'
	make linkcheck -e SPHINXOPTS='-aE -W -Q'
	@echo SUCCESS
