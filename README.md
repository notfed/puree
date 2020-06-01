# PUREE
## Password-based Uniform-Random-Equivalent Encryption

### What is PUREE?

PUREE is a disk encryption header format and `puree` is a command-line tool suite which, together, allow you to password-protect disk devices, using full-disk encryption, in such a way such that the entire disk is indistinguishable from random data. Notably, this occurs without the need to store any associated data on a separate disk. The on-disk format is simple, secure, and extensible, while the command-line tool is convenient and simple to use.

### What are the prerequisites?

While the PUREE disk format is platform-independent, the `puree` command-line tool currently only supports Linux.

In addition, the following system libraries must be installed:

    sudo apt install python3 python3-pip python3-setuptools libsodium23 # Debian, Ubuntu
    sudo dnf install python3 python3-pip python3-setuptools libsodium # Red Hat, Fedora

### How do I install `puree`?
Install `puree` with:

    sudo python3 -m pip install puree

(Generally, using `sudo` to perform `pip install` is not recommended. However, because disk devices usually require root permission to access, `puree` is often invoked with `sudo`—and `sudo` tends to hide userspace-installed Python packages from the `PATH`.  If you like, you may install `puree` into `~/.local`  by instead running "`python -m pip install --user puree pysodium argon2-cffi`", but be aware you'll likely get an error if you invoke `puree` via `sudo`.)

### How do I use it?

Let's go through the complete flow, from formatting a device with PUREE all the way to mounting it.

(WARNING: By encrypting a device with PUREE, you will be wiping all data from the disk.)

We'll encrypt device `/dev/sdz` with `AES-256` in `XTS` mode.

First, format the disk with PUREE:

    sudo puree format /dev/sdz aes256-xts-plain64

(You will be prompted for a password. PUREE will require you to prefix your password with a "parameter char"; see the "Choosing a parameter char" section below for an explanation.)

Your device should now be encrypted.

Next, you'll need to "map" your encrypted disk device to a new virtual device:

    sudo puree map /dev/sdz /dev/mapper/sdz

(You will be prompted to enter the disk's password.)

The virtual device should now be available at `/dev/mapper/sdz`; you can now treat `/dev/mapper/sdz` as you would a normal disk device.  

For example, to format it with a filesystem, then mount it:

    sudo mkfs.ext4 /dev/mapper/sdz
    sudo mount /dev/mapper/sdz /mnt

You now have an encrypted fileystem available at `/mnt`.

To unmap the device, run:

    sudo puree unmap /dev/mapper/sdz

To prove to yourself that the disk is encrypted, try running `sudo hexdump -C /dev/sdz | less`, and you'll see something like this:

```
00000000  3ac41e42 da074126 fb9d4c6a 01a15f56  |...B..A&..Lj.._V|
00000010  c71c6c47 3a891a07 77af909a 4efb1a8f  |..lG:...w...N...|
00000020  72fc3eac 1766db1d 55d2c0cd 14a666bd  |r.>..f..U.....f.|
00000030  5592d610 bbc3ad81 46eb2bf7 cec566b6  |U.......F.+...f.|
00000040  8c44df17 8868323d d175458d 4327d107  |.D...h2=.uE.C'..|
00000050  6dbf3af8 11083156 dd3bb235 83826b62  |m.:...1V.;.5..kb|
00000060  fad3a02d 48acebc5 7b79ce68 ec9e68f1  |...-H...{y.h..h.|
00000070  4c5daf93 1a2bb71f ace7f417 ca627d05  |L]...+.......b}.|
00000080  39568ce6 5ec12f58 38c056d3 d682d728  |9V..^./X8.V....(|
00000090  446df278 d823fee0 ff2f4c04 434b5f5e  |Dm.x.#.../L.CK_^|
000000a0  bc425830 55c455cd b4439385 c59bf3fd  |.BX0U.U..C......|
000000b0  62019305 a5f38ce9 12c0c138 76f31f1b  |b..........8v...|
000000c0  8e67545a e3abf95a 2247fc0c 5c55558c  |.gTZ...Z"G....U.|
000000d0  01c62344 8fbb35df 80b313da 63269760  |..#D..5.....c&.`|
000000e0  4dfbd88d d32a1179 e4038d7c 3c4412eb  |M....*.y...|<D..|
000000f0  c856ecfe 15e5c4a5 d7f12165 628c05b8  |.V........!eb...|
00000100  6c00f7e2 dcb39dce dff67d1d e9551eaa  |l.........}..U..|
00000110  d9e24fd6 0f42b399 ed18adec 4de8912a  |..O..B......M..*|
00000120  2316e413 1712a0a7 044b96d3 154d1b2f  |#........K...M./|
00000130  67a62365 6f15d733 f4541fc7 8781bfd3  |g.#eo..3.T......|
```

Now that you've done that, be aware that, to truly keep your disk indistinguishable from random, you should first complete wipe the disk with random data:

    sudo puree destroy /dev/sdz

Then repeat the previous steps. (Previously, we left this step out as it tends to take a while.)

#### Choosing a parameter char

`puree` encrypts disks in such a way that its primary key is derived using the [Argon2](https://en.m.wikipedia.org/wiki/Argon2) password-key derivation function.  In order to calculate a derived key from a password, however, a few parameters are required:

1. Parallelism: the maximum number of parallel CPU threads
2. Memory: the amount of RAM required
3. Iterations: multiplier on amount of time required

One goal of PUREE is that the disk must be indistinguishable from random data. This means these parameters can not be stored on the disk.  Instead, PUREE stores these parameters in the password.  Every PUREE password must be prefixed with a special character, called the "parameter char". Current valid values are:

- `'b' => parallelism: 1,  memory: 75MiB,  iterations: 1`
- `'c' => parallelism: 1,  memory: 250MiB, iterations: 1`
- `'d' => parallelism: 4,  memory: 250MiB, iterations: 4`
- `'e' => parallelism: 1,  memory: 1GiB,   iterations: 1`
- `'f' => parallelism: 4,  memory: 1GiB,   iterations: 4`
- `'g' => parallelism: 1,  memory: 4GiB,   iterations: 1`
- `'h' => parallelism: 4,  memory: 4GiB,   iterations: 4`
- `'i' => parallelism: 1,  memory: 16GiB,  iterations: 1`
- `'j' => parallelism: 4,  memory: 16GiB,  iterations: 4`

Also:

- `'a' => simply hash the salt and password with blake2b`

As CPU and RAM become cheaper, more parameter chars will be added to this table.
