#!/usr/bin/env python3
"""Regenerates dark_mode.svg / light_mode.svg (profile card with ASCII portrait).
Usage: python3 build_svgs.py        (needs: pip install numpy opencv-python-headless)
Source photo: assets/portrait_source.png (oval crop is auto-detected: rows 250-1157)."""
import numpy as np, cv2
from xml.sax.saxutils import escape

COLS, FONT, CHAR_W, LINE_H = 100, 8, 4.4, 9
RAMP = " .,:;-=+*#%@"

def portrait(invert):
    im = cv2.imread('assets/portrait_source.png')[250:1157]
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); h, w = g.shape
    m = np.zeros((h, w), np.uint8)
    cv2.ellipse(m, (w//2, h//2), (w//2-4, h//2-4), 0, 0, 360, 255, -1)
    g = cv2.bilateralFilter(g, 9, 40, 9)
    fr = g[190:600, 190:500].astype(float)
    lo, hi = np.percentile(fr, 2), np.percentile(fr, 97)
    x = np.clip((g.astype(float)-lo)/(hi-lo), 0, 1) ** 0.6
    x = 0.14 + 0.86*x   # lift shadows so hair keeps texture
    yy, xx = np.mgrid[0:h, 0:w]
    fade = np.clip(1.25-1.2*(((xx-w*.5)/(w*.46))**2+((yy-h*.5)/(h*.52))**2), .3, 1)
    if not invert: x = x*fade
    else: x = 1-(1-x)*fade   # keep fade pointing to 'empty' on light bg
    H = int(COLS*h/w*0.5)
    s = cv2.resize(x, (COLS, H), interpolation=cv2.INTER_AREA)
    s = np.clip(s+0.8*(s-cv2.GaussianBlur(s, (0, 0), 1.0)), 0, 1)
    mm = cv2.resize(m, (COLS, H), interpolation=cv2.INTER_AREA) > 127
    s = np.clip((s-s[mm].min())/(s[mm].max()-s[mm].min()), 0, 1)
    if invert: s = 1-s
    return [''.join(RAMP[min(len(RAMP)-1, int(s[y, c]*len(RAMP)))] if mm[y, c] else ' '
                    for c in range(COLS)) for y in range(H)]

W_LINE = 62
CW2 = 8.6
def kv(k, v):
    dots = '.'*max(2, W_LINE-len(k)-len(v)-4)
    return f'<tspan class="cc">. </tspan><tspan class="key">{escape(k)}</tspan>:<tspan class="cc"> {dots} </tspan><tspan class="value">{escape(v)}</tspan>'
def head(t): return f'{escape(t)} ' + '—'*(W_LINE-len(t)-2)

INFO = [
 ('head', 'shikhar@dixit'),
 ('kv', 'Role', 'Full-Stack · Security · AI/RAG'),
 ('kv', 'Now', 'Intern @ NTRO, Govt. of India'),
 ('kv', 'Also', 'Full Stack Dev @ SGCA Technologies'),
 ('kv', 'Previously', 'SDE Intern @ Physics Wallah'),
 ('kv', 'Education', 'B.Tech CSE (AIML), IILM Univ. — 2028'),
 ('kv', 'Leadership', 'VP, E-Cell · SIH 2025 Grand Finalist'),
 ('blank',),
 ('head', 'Stack'),
 ('kv', 'Languages', 'Python, C, TypeScript, JavaScript'),
 ('kv', 'Backend', 'FastAPI, REST APIs, MySQL, MongoDB'),
 ('kv', 'Frontend', 'React, Vite, Tailwind CSS'),
 ('kv', 'AI', 'RAG pipelines, embeddings, vector search'),
 ('kv', 'Security', 'Nmap, Nuclei, Nikto, OpenVAS, CVE/CVSS'),
 ('kv', 'Tools', 'Git, Linux, macOS'),
 ('blank',),
 ('head', 'Projects'),
 ('kv', 'CyberRakshak', 'AI-assisted vulnerability analysis'),
 ('kv', 'SewaSetu', 'reporting platform, ~30% faster'),
 ('kv', 'Seedify', 'co-authored research paper'),
 ('blank',),
 ('head', 'Contact'),
 ('kv', 'Portfolio', 'shikhardixit.framer.website'),
 ('kv', 'Email', 'dixitshikhar719@gmail.com'),
 ('kv', 'Phone', '+91 88649 51603'),
 ('kv', 'LinkedIn', 'shikhar-dixit-27214931a'),
 ('kv', 'LeetCode', 'codewithshikhar'),
 ('kv', 'Codeforces', 'devwithshikhar'),
 ('blank',),
 ('head', 'Current'),
 ('kv', 'Focus', 'AI memory forensics @ NTRO · CORTEX'),
]

THEMES = {
 'dark_mode.svg':  dict(bg='#161b22', fg='#c9d1d9', key='#ffa657', val='#a5d6ff', cc='#616e7f', art='#c9d1d9', inv=False),
 'light_mode.svg': dict(bg='#f6f8fa', fg='#24292f', key='#953800', val='#0a3069', cc='#c2cfde', art='#24292f', inv=True),
}

def build(fn, t):
    art = portrait(t['inv'])
    art_h = len(art)*LINE_H
    info_x = int(15+COLS*CHAR_W+30)
    width = info_x + int((W_LINE+1)*CW2) + 25
    height = max(art_h, len(INFO)*20) + 50
    top = 30 + (height-30-art_h)//2 - 10
    out = [f"<?xml version='1.0' encoding='UTF-8'?>",
      f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width}px" height="{height}px" font-size="16px">',
      "<style>\n@font-face {\nsrc: local('Consolas'), local('Consolas Bold');\nfont-family: 'ConsolasFallback';\nfont-display: swap;\n-webkit-size-adjust: 109%;\nsize-adjust: 109%;\n}",
      f".key {{fill: {t['key']};}}\n.value {{fill: {t['val']};}}\n.cc {{fill: {t['cc']};}}\ntext, tspan {{white-space: pre;}}\n</style>",
      f'<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>',
      f'<text fill="{t["art"]}" class="ascii" font-size="{FONT}px">']
    for i, l in enumerate(art):
        out.append(f'<tspan x="15" y="{top+i*LINE_H}" textLength="{COLS*CHAR_W:.0f}" lengthAdjust="spacing">{escape(l.ljust(COLS))}</tspan>')
    out.append('</text>')
    out.append(f'<text x="{info_x}" y="30" fill="{t["fg"]}">')
    y = 30
    for row in INFO:
        if row[0] == 'head': out.append(f'<tspan x="{info_x}" y="{y}" textLength="{(W_LINE-1)*CW2:.0f}" lengthAdjust="spacing">{head(row[1])}</tspan>')
        elif row[0] == 'kv': out.append(f'<tspan x="{info_x}" y="{y}" textLength="{(W_LINE+1)*CW2:.0f}" lengthAdjust="spacing">{kv(row[1], row[2])}</tspan>')
        y += 20
    out.append('</text>\n</svg>\n')
    open(fn, 'w', encoding='utf-8').write('\n'.join(out))
    print(fn, width, height)

for fn, t in THEMES.items(): build(fn, t)
