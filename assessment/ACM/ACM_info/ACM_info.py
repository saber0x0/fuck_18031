import re, pathlib, glob

regex = re.compile(r'(E\.Info\.\S*(?:ACM|acm)\S*)', re.I | re.S)
for f in glob.glob('../../../18031/18031-*.txt'):
    print(f'=== {f} ===')
    for m in sorted(set(regex.findall(pathlib.Path(f).read_text(encoding='utf-8')))):
        print(m)