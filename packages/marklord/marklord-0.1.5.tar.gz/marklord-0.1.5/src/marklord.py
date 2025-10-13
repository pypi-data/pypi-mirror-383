#! /usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont, ImageChops
from pdf2image import convert_from_path
import math
import functools
import random
import os
import argparse
import logging

log = logging.getLogger("MarkLord")
logging.basicConfig()
log.setLevel(1)

def file_size_human(fname):
    size = os.path.getsize(fname)
    for unit in ['B', 'KB', 'MB', 'GB' ]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@functools.cache
def get_noise(X,Y):
    import numpy as np
    a = np.random.randint(60,200, (Y,X,3), dtype=np.uint8)
    return Image.fromarray(a).convert("RGBA")

def font_exists(fontname):
    try:
        ImageFont.truetype(fontname)
    except:
        return False
    else:
        return True


def filigrane(img, text, fontname=None, angle=30, lines_nb=10, interlining=2, color=None,alpha=150, sep="   ",noise=True): 
    if fontname and font_exists(fontname):
        load_font = lambda sz: ImageFont.truetype(fontname, sz)
    else:
        load_font = lambda sz: ImageFont.load_default(sz)
    if color is None:
        color = (155,155,155,alpha)
    X,Y = img.size
    X2 = Y2 = int(math.ceil(math.sqrt(X**2+Y**2)))
    txt = Image.new("RGBA",(X2,Y2), (155,255,255,0))
    fntsize = 10
    muly = lines_nb
    while True:
        fnt = load_font(fntsize)
        _,_,stx,sty=fnt.getbbox(text)
        if sty*(interlining+1)*lines_nb >= Y2:
            break
        fntsize += 1
    mulx = X2//sty+1
    one_line = sep.join([text]*mulx)
    k = len(text)+len(sep)
    all_lines = [one_line[-random.randint(0,k):] + one_line for _ in range(muly+3)]
    complete_text = ("\n"*(interlining+1)).join(all_lines)
    d = ImageDraw.Draw(txt)
    d.text((10,10),complete_text, font=fnt, fill=color)
    if noise:
        txt = ImageChops.multiply(get_noise(X2,Y2),txt)
    txt = txt.rotate(angle).crop( ((X2-X)//2, (Y2-Y)//2, (X2-X)//2+X, (Y2-Y)//2+Y) )
    out = Image.alpha_composite(img.convert("RGBA"),txt).convert("RGB")
    return out

def percent_type(value):
    ivalue = int(value.strip("%"))
    if not 0 <= ivalue <= 100:
        raise argparse.ArgumentTypeError(f"Value must be between 0 and 100, got [{ivalue}]")
    return ivalue


def color_type(value):
    hvalue = value.strip("#")
    if "," in hvalue:
        parts = hvalue.split(',')
        if len(parts) != 4:
            raise argparse.ArgumentTypeError("Must provide exactly 4 integers separated by commas")
        ints = []
        for part in parts:
            try:
                ivalue = int(part)
            except:
                raise argparse.ArgumentTypeError(f"Value must be an integer, got [{part}]")
            if not 0 <= ivalue <= 255:
                raise argparse.ArgumentTypeError(f"Value must be between 0 and 255, got [{ivalue}]")
            ints.append(ivalue)
    else:
        try:
            ivalue=int(hvalue, 16)
        except:
            raise argparse.ArgumentTypeError(f"Value must be an integer, got [{value}]")
        if ivalue >= 2**32:
            raise argparse.ArgumentTypeError(f"Value [{value}] is too large for a 32 bit color")
        ints = tuple((ivalue >> (8*i)) & 0xff for i in range(3,-1,-1))
    return tuple(ints)



def font_type(value):
    if font_exists(value):
        return value
    raise argparse.ArgumentTypeError(f"Cannot open font [{value}]")


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o")
    parser.add_argument("--font-name", "-f", type=font_type) 
    parser.add_argument("--angle", "-a", default=30)
    parser.add_argument("--watermark_lines", "-l", default=10)
    parser.add_argument("--interlining", "-I", default=2)
    parser.add_argument("--separator", "-s", default="   ")
    parser.add_argument("--no-noise", action="store_true", default=False)
    parser.add_argument("--color", "-c", type=color_type, help="RGBA color (hexa or 4 comma separated decimal numbers from 0 to 255)")
    parser.add_argument("--alpha", "-A", type=percent_type, help="transparency coefficient between 0%% and 100%%", default=75)
    parser.add_argument("--quiet", "-q", action="count", default=0)
    parser.add_argument("input", type=argparse.FileType('rb'))
    parser.add_argument("text", nargs="+")
    options = parser.parse_args(args)

    log.setLevel(20+10*options.quiet)

    if options.font_name is None:
        # Most probable font to exist on any system
        # Pillow's embedded default font will be used if not found 
        options.font_name = "DejaVuSerif.ttf" 

    log.info(f"Opening [{options.input.name}] ({file_size_human(options.input.name)})")

    options.text = " ".join(options.text)
    log.info(f"Watermarking [{options.text}]")

    base,ext = os.path.splitext(options.input.name)
    apply_wm = lambda im: filigrane(im, options.text,
                                     fontname=options.font_name, interlining=options.interlining, angle=options.angle,
                                     lines_nb=options.watermark_lines, sep=options.separator, noise=not options.no_noise,
                                     color=options.color, alpha=options.alpha)


    if not options.output:
        options.output = base+"-wm"+ext
        i=0
        while os.path.exists(options.output):
            i += 1
            options.output = base+f"-wm{i}"+ext

    if ext.lower() == ".pdf":
        pages = convert_from_path(options.input.name)
        log.info(f"PDF file with {len(pages)} pages")
        wmpages = [apply_wm(p) for p in pages]
        wmpages[0].save(options.output, append_images=wmpages[1:],save_all=True)
    else:
        im = Image.open(options.input)
        wim = apply_wm(im)
        wim.save(options.output)
    log.info(f"Result saved to [{options.output}] ({file_size_human(options.output)})")


if __name__ == "__main__":
    main()
