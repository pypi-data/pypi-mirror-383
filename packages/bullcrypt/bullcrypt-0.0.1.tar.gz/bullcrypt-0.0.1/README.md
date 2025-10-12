<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>🎯 BullCrypt</h1>
</div>

<hr />

<div align="center">

[💼 Purpose](#purpose)

</div>

<hr />

# Purpose

Inspired by capture-the-flag (CTF) competitions, BullCrypt provides a rapid means to decrypt ciphertext from files.

Currently, BullCrypt supports the following algorithms:
- Fernet

# Usage

You can install BullCrypt from [PyPI](https://pypi.org/project/bullcrypt/):

```commandline
python -m pip install bullcrypt
```

When installed, a `bullcrypt` command is available and usage information is available with the `--help` flag:

```commandline
bullcrypt --help
```

Generally, to decrypt ciphertext, BullCrypt requires that you specify a:
- **File Parsing Strategy** (Required—Select one):
  - Ciphertext Per Line (--line): Interpret non-blank lines in files as encoded ciphertext, such as when each line is a separate Base64 ciphertext.
  - Chunked (--chunked): Each file contains one ciphertext, but may be chunked up with newline delimiters.
  - Raw (--raw): Each file contains one ciphertext which should be interpreted as bytes.
- **Plaintext Encoding** (Optional-Select one):
  - Base64 (--base64): Interpret plain-text content as Base64 using the standard alphabet.
  - Base64URL (--base64url): Interpret plain-text content as Base64 with the filesystem and URL-safe alphabet.
  - Base32 (--base32): Interpret plain-text content as Base32. Does not accept the lowercase alphabet and does not support mapping at this time.
  - Base32hex (--base32hex): Interpret plain-text content ase Base32 using the extended HEX alphabet. Does not accept the lowercase alphabet at this time.
  - Base16 (--base16): Interpret plain-text content ase Base32. Does not accept the lowercase alphabet.
  - Plaintext (--plain): Interpret plain-text content as simply plain text.

Algorithms may also require certain options, such as keys.

Decoding options primarily depend on the layout of your ciphertext. You may also choose to traverse through directories 
using `--recursive`. The following examples leverage the Fernet algorithm.

### Raw File Parsing

When raw file parsing is selected, files are opened and read as bytes. As a result, encoding options are ignored. You
should use raw file parsing if the ciphertext is generally not meant to be human-readable at all and is not normalized.
For example, if chunking was performed (ex. only 140 characters per line), an operation frequently done with Base64, you
may find chunked mode more helpful.

With the Fernet algorithm, raw file parsing can be done when the entire ciphertext is on one line in the file. This is 
not mandatory because it encrypts into ASCII characters.

File:

```
gAAAAABo6pg_q-T_D8bfHRk8i0tHpv6WOZvmW9VfTB0WDvlyTb-2ACVxl27pLQoKnvzQtjRxOKUDAgZQ7CG9__I-fC_uic5uW70CUIlPwyS3I1M7UKqm8Y-HyBQQeu5I2jHBn776AlxN
```

Command:

```shell
bullcrypt --raw --fernet.key "ZLNIc8ScmrGNNKPQILQR67xZcTdn_zID2VOeOXayjA0=" fernet /path/to/ciphertext
```

### Chunked File Parsing

Chunked file parsing is useful when each file contains only one ciphertext, but the ciphertext is split across many 
lines, often done when it is large and in ASCII characters, such as in the case of Base64. BullCrypt will strip out
all line feed characters and join the strings back together to reconstruct the ciphertext as it was originally.

File:
```
gAAAAABo6pkxtsC2mQhmkjVr8qYFU9EvtmYpY_Qwbz_2OQxiv-1p3lxu_PQQ6T90SEGNOT
lFLaTAUP9HPaboglmsBDgqRqlburZHeDLfHrj-5QJJBkgvaWtBi5sqREGMP2hTAhtN3ewy
```

Command:

```shell
bullcrypt --chunked --plain --fernet.key "xegqwfrOEToIO9s3Uh-ft8pK6W36ucuQZ7shlW31e1Q=" fernet /path/to/ciphertext
```

Notice how `--plain` was added. This is because the ciphertext is in the original format as produced by the Fernet 
algorithm and was not transformed (such as if it was Base64-encoded).

### Line File Parsing

Line file parsing can be used when there are many ciphertexts in a file, each on their own line. BullCrypt will ignore
blank lines.

File:
```
gAAAAABo6pnv7FG_f0MRalPBnN-TAZqAsA7GqoOzUKbdXJY1cR950e8-Ltv_tA4ezDhG0HDxS3eqwxzRF9008S4_d_paMZgmUg==
gAAAAABo6pn34vh-8UME5yowIEvpuKMqkLmD1BnlON2c59Csqr1J_L3X30Aw9Bdtr7fodNBq-JJhqbZCJtOdo1JBA0vSMYA5yA==
gAAAAABo6pn9oxXe3xUR5sWYXYL2r6LQFmxWEVxOts-f0zp7PGnaPNNsHrrhBL6xBanTZ8Qj6dsAVz2LQdUlFXXnBRjowEND1A==
gAAAAABo6poC-QaCWpv7bn55qTfPtLndexa-4EiTKvU1RIuAE8StnMIzzPVfpaIcZbWh1U42UoW4VkC1M9pztlf6BvLOTsoQhg==
gAAAAABo6poIMY724MTyadlpTTCRe_v31AKt7bpbCp1KIsbBv0ESbdsU6-lrqkOqvXQhb7vuCWL2lqX71GhBN6GzsS7LDYWlZw==
```

Command:

```shell
bullcrypt --line --plain --fernet.key "__v9Onuy1wgYTueMJ5BhHc4UnSYYuNuQUkUyLZtA0G8=" fernet /path/to/ciphertext
```

Once again, `--plain` was added because each line is as provided by the Fernet algorithm.