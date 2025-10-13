# MarkLord

MarkLord is a tool to add a visible watermark to images or PDF files
on documents (e.g. ID card, salary slips, etc. ) you need to send to
third parties.  If the said third party is victim of a data breach, it
will be more difficult for attackers to use those documents to steal
your identity.  Also if you put the name of the third party into the
watermark, you can identify the source of the leak, or the third party
that shared or sold your files without your consent.

## Installation

### From PyPI

```bash
pip install marklord
```

### From GitHub

```bash
git clone https://github.com/secdev/marklord.git
cd  marklord
pip install .
```

## Usage

```
usage: marklord [-h] [--output OUTPUT] [--font-name FONT_NAME] [--angle ANGLE] [--watermark_lines WATERMARK_LINES] [--interlining INTERLINING] [--separator SEPARATOR] [--no-noise] [--color COLOR] [--alpha ALPHA] [--quiet] input text [text ...]

positional arguments:
  input
  text

options:
  -h, --help            show this help message and exit
  --output, -o OUTPUT
  --font-name, -f FONT_NAME
  --angle, -a ANGLE
  --watermark_lines, -l WATERMARK_LINES
  --interlining, -I INTERLINING
  --separator, -s SEPARATOR
  --no-noise
  --color, -c COLOR     RGBA color as 4 comma separated decimal numbers from 0 to 255
  --alpha, -A ALPHA     transparency coefficient between 0 and 255
  --quiet, -q
```


## Examples

```
$ marklord idcard.jpg "only for ACME company 2025-12-04"
INFO:MarkLord:Opening [/home/specimen/idcard.jpg] (53.2 KB)
INFO:MarkLord:Watermarking [only for ACME company 2025-12-04]
INFO:MarkLord:Result saved to [/home/specimen/idcard-wm.jpg] (60.1 KB)
```

![watermarked image](https://github.com/secdev/marklord/raw/main/doc/assets/idcard_wm.jpg)

