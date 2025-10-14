.PHONY: build docs dist

full-test:
	./test-full_prerelease.py

test:
	python3 ./test.py -bv

test-4.8:
	BERKELEYDB_DIR=/usr/local/BerkeleyDB.4.8 python3 ./test.py -bv

test-5.3:
	BERKELEYDB_DIR=/usr/local/BerkeleyDB.5.3 python3 ./test.py -bv

test-6.2:
	BERKELEYDB_DIR=/usr/local/BerkeleyDB.6.2 python3 ./test.py -bv

test-18.1:
	BERKELEYDB_DIR=/usr/local/BerkeleyDB.18.1 python3 ./test.py -bv

dist: clean docs
	YES_I_HAVE_THE_RIGHT_TO_USE_THIS_BERKELEY_DB_VERSION=1 \
		DISTUTILS_DEBUG=1 \
		./setup.py sdist

clean: docs-clean
	rm -rf build dist __pycache__ tests/__pycache__

docs-clean:
	cd docs && $(MAKE) clean

docs:
	cd docs && $(MAKE) html
