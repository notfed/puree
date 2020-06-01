default:
install-deps:
	sudo apt install python3 python3-pip python3-setuptools libsodium23 || sudo dnf install python3-pip python3-setuptools libsodium
install:
	sudo python3 -m pip install puree
wheel:
	rm -fr dist/ build/
	python3 setup.py sdist bdist_wheel
test:
	bash tests/test1-write-read.sh
