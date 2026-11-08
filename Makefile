.PHONY: gen test
gen:
	python3 tools/gen_colorschemes.py
test:
	python3 -m unittest discover -s tests -v
