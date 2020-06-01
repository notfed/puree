#!/bin/bash
set -e
DIR=$(cd "$(dirname "$0")" && pwd)
TESTDIR=$DIR/test-results
PUREEDIR=$(cd $DIR/.. && pwd)
PUREE=$PUREEDIR/puree
mkdir -p $TESTDIR
cd $PUREEDIR
LOOPDEVICE=""
echo '---- Prompt for sudo ----'
sudo echo "prompt_for_sudo" > /dev/null
if [ $? -ne 0 ]; then
	echo "Can't run test: need sudo password"
	exit 2
fi
cleanup() {
	if [ -b /dev/mapper/puree-test-device ]; then
	    sudo dmsetup remove puree-test-device 2>/dev/null || true
	fi
	if [ -f $TESTDIR/LOOPDEVICE ]; then
	    losetup -d `cat $TESTDIR/LOOPDEVICE` 2>/dev/null || true
	fi
}
cleanup

echo '---- Create an empty fake disk, and a fake password ----'
cat /dev/zero | head -c 3145728 > $TESTDIR/fakedisk # 3MiB
echo -n "asdf" > $TESTDIR/fakepassword

# ---- Mount the fake disk as a device ----
LOOPDEVICE=`sudo losetup $TESTDIR/fakedisk --find --show`
echo -n $LOOPDEVICE > $TESTDIR/LOOPDEVICE
sudo chown $UID $LOOPDEVICE

echo '---- Format the device ----'
$PUREE format -v -f $LOOPDEVICE aes256-cbc-essiv-sha256 -p $TESTDIR/fakepassword 

echo '---- Map the device ----'
#sudo dmsetup create puree-test-device --table "0 1 crypt aes-cbc-essiv:sha256 8b7acdddef30fc2aba58fb47c227a6b5fb8e2b90c8b42d960becaf3f7b125b62 0 $LOOPDEVICE 1"
sudo $PUREE map $LOOPDEVICE /dev/mapper/puree-test-device -p $TESTDIR/fakepassword 
sudo chown $UID /dev/mapper/puree-test-device
test -b /dev/mapper/puree-test-device && cat /dev/zero | head -c 512 > /dev/mapper/puree-test-device

echo '==== TEST RESULTS ===='

echo '---- hexdump /dev/mapper/puree-test-device ----'
hexdump /dev/mapper/puree-test-device
echo '---- hexdump $LOOPDEVICE ----'
hexdump $LOOPDEVICE

echo '---- SUCCESS ----'
echo '==== END OF TEST RESULTS ===='
cleanup

