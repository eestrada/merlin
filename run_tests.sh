#!/bin/sh

function echoerr()
{
	echo "$@" 2>&1
}

echoerr "Warning: version 2.7 is the only supported version of python2.x."
echoerr "Warning: version 3.2 is the lowest supported version of python3.x."
echoerr "If your installed versions of python do not comply with this, this test suite is unlikely to work."
echoerr

if which python2 >/dev/null ; then
	py2v=$(python2 --version 2>&1)
	echoerr "Running python test suite with ${py2v}..."
	echoerr
	python2 testsuite.py "$@"
else
	echoerr "Python2 could not be found."
fi

if which python3 >/dev/null ; then
	py3v=$(python3 --version 2>&1)
	echoerr "Running python test suite with ${py3v}..."
	echoerr
	python3 testsuite.py "$@"
else
	echoerr "Python3 could not be found."
fi

