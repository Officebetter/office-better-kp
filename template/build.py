import sys, base64, io, os, glob, re
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(HERE)
sys.path.insert(0,HERE)
from data import *  # дані конкретної КП: data.py (див. data_example.py)
import data as _d, datetime
KIDS = getattr(_d, 'KIDS', [])          # [(код, назва, вага, склад, кількість, ціна за шт), ...]
VARIANTS = getattr(_d, 'VARIANTS', [])
QTY = getattr(_d, 'QTY', 0)
BUDGET = getattr(_d, 'BUDGET', None)
KP_DATE = getattr(_d, 'KP_DATE', datetime.date.today().strftime('%d.%m.%Y'))
from PIL import Image, ImageChops

def b64(path): return base64.b64encode(open(path,'rb').read()).decode()

# фото з репозиторію: файл, що починається з коду (терпимо до зайвих символів у назві)
photos = {}
for f in glob.glob(os.path.join(REPO,'products','*')):
    m = re.match(r'(NY-\d{3})', os.path.basename(f))
    if not m: continue
    im = Image.open(f).convert('RGBA')
    bg = Image.new('RGBA', im.size, (255,255,255,255)); bg.alpha_composite(im); im = bg.convert('RGB')
    diff = ImageChops.difference(im, Image.new('RGB', im.size, (255,255,255)))
    bbox = diff.point(lambda p: 255 if p > 18 else 0).getbbox()
    if bbox: im = im.crop(bbox)
    s = max(im.size); pad = int(s*0.06)
    sq = Image.new('RGB', (s+2*pad, s+2*pad), (255,255,255)); sq.paste(im, ((s+2*pad-im.width)//2, (s+2*pad-im.height)//2))
    sq.thumbnail((420,420), Image.LANCZOS)
    buf = io.BytesIO(); sq.save(buf, 'JPEG', quality=86); photos[m.group(1)] = base64.b64encode(buf.getvalue()).decode()

mascot = b64(os.path.join(REPO,'brand','mascot-elf.png'))
logo_svg = b64(os.path.join(REPO,'brand','logo.svg'))
fdir = os.environ.get('KP_FONTS','/tmp/fnt/package/files')
if not os.path.isdir(fdir):  # шрифт Montserrat завантажується автоматично при першому запуску
    import subprocess
    os.makedirs('/tmp/fnt', exist_ok=True)
    subprocess.run('npm pack @fontsource/montserrat@5.0.19 -q >/dev/null 2>&1 && tar xzf fontsource-montserrat-5.0.19.tgz', shell=True, cwd='/tmp/fnt', check=True)
fonts = ''
for w in (400,500,600,700,800,900):
    for sub, rng in (('cyrillic','U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116'),('latin','U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD')):
        fonts += f"@font-face{{font-family:'Montserrat';font-weight:{w};font-style:normal;src:url(data:font/woff2;base64,{b64(f'{fdir}/montserrat-{sub}-{w}-normal.woff2')}) format('woff2');unicode-range:{rng};}}\n"

def money(x): return f"{x:,.0f}".replace(',', '\u202f')
def price(c): return round(I[c][4]*MULT)
CHECK = '<svg viewBox="0 0 40 40" class="chk"><rect x="2" y="6" width="30" height="30" rx="7" fill="none" stroke="#07002C" stroke-width="3.5"/><path d="M9 20 L17 29 L37 4" fill="none" stroke="#6259ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LOGO = f'<img class="logo" src="data:image/svg+xml;base64,{logo_svg}" alt="Office Better">'

import math, random
BULB = ['#b82266','#6259ff','#2f2987','#ccf2ff','#b82266','#6259ff']
def garland():
    # гірлянда по верхньому краю: провисаючі дуги з кульками-лампочками
    W, swags, d = 297, 7, 5.2
    out = ['<svg class="garland" viewBox="0 0 297 16" preserveAspectRatio="none">']
    step = W / swags; k = 0
    for i in range(swags):
        x0, x1 = i*step, (i+1)*step; cx, cy = (x0+x1)/2, 1.2 + d*2
        out.append(f'<path d="M{x0:.1f},1.2 Q{cx:.1f},{cy:.1f} {x1:.1f},1.2" fill="none" stroke="#2f2987" stroke-width=".45" stroke-opacity=".55"/>')
        for t in (0.22, 0.5, 0.78):
            x = (1-t)**2*x0 + 2*(1-t)*t*cx + t**2*x1; y = (1-t)**2*1.2 + 2*(1-t)*t*cy + t**2*1.2
            c = BULB[k % len(BULB)]; k += 1
            stroke = ' stroke="#9fd9f0" stroke-width=".3"' if c == '#ccf2ff' else ''
            out.append(f'<rect x="{x-0.75:.2f}" y="{y-0.2:.2f}" width="1.5" height="1.3" rx=".3" fill="#9497b3"/>'
                       f'<ellipse cx="{x:.2f}" cy="{y+2.6:.2f}" rx="1.45" ry="2.1" fill="{c}"{stroke}/>'
                       f'<ellipse cx="{x-0.45:.2f}" cy="{y+2.0:.2f}" rx=".35" ry=".6" fill="#fff" fill-opacity=".7"/>')
    out.append('</svg>')
    return ''.join(out)
GARLAND = garland()

def flake(x, y, r, op):
    arms = ''.join(f'<g transform="rotate({a} {x} {y})"><line x1="{x}" y1="{y}" x2="{x}" y2="{y-r}"/><line x1="{x}" y1="{y-r*.55}" x2="{x-r*.25}" y2="{y-r*.78}"/><line x1="{x}" y1="{y-r*.55}" x2="{x+r*.25}" y2="{y-r*.78}"/></g>' for a in range(0,360,60))
    return f'<g stroke="#6259ff" stroke-opacity="{op}" stroke-width="{r*.09:.2f}" stroke-linecap="round">{arms}</g>'
def snow(points):
    return '<svg class="snow" viewBox="0 0 297 210">' + ''.join(flake(*p) for p in points) + '</svg>'
SNOW_TITLE = snow([(78,62,3.4,.16),(86,150,3.2,.13),(16,140,2.6,.12),(178,30,2.6,.14),(208,22,3,.14),(262,30,2.4,.16)])
SNOW_SPEC = snow([(70,27,2.8,.14),(96,31,3.2,.16),(120,21,2.4,.14)])

def bauble(x, length, r, color, cap='#c9a24b'):
    return (f'<line x1="{x}" y1="0" x2="{x}" y2="{length}" stroke="#2f2987" stroke-opacity=".4" stroke-width=".3"/>'
            f'<rect x="{x-1}" y="{length-0.6}" width="2" height="1.4" rx=".3" fill="{cap}"/>'
            f'<circle cx="{x}" cy="{length+r+0.4}" r="{r}" fill="{color}"/>'
            f'<path d="M{x-r*.8},{length+r+0.4} Q{x},{length+r*1.5+0.4} {x+r*.8},{length+r+0.4}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".35"/>'
            f'<circle cx="{x-r*.35}" cy="{length+r*.6+0.4}" r="{r*.22}" fill="#fff" fill-opacity=".6"/>')
BAUBLES = ('<svg class="baubles" viewBox="0 0 297 40">' + bauble(118,14,3.4,'#b82266') + bauble(132,22,2.6,'#6259ff') + bauble(145,10,2.2,'#ccf2ff') + bauble(158,18,3,'#2f2987') + '</svg>')

def thumb(c, cls='ph'):
    if c in photos: return f'<div class="{cls}"><img src="data:image/jpeg;base64,{photos[c]}" alt=""></div>'
    label = I[c][3] if c in I else 'Набір'
    return f'<div class="{cls} noph"><span>{label}</span></div>'

def storage_line(codes):
    t = min(I[c][8] for c in codes)
    return "Зберігання в офісі без холодильника" if t >= 20 else "Зберігати в прохолодному місці, до +18°C"

def footer(codes=None, totals=None, kids=None):
    m = MANAGER
    perks = ['100% бюджету — в делікатеси, без переплати за коробку', 'Договір і документи з ПДВ']
    if codes: perks.insert(1, storage_line(codes))
    if kids: perks = ['Від 10 шт кожного набору', 'Що більше наборів — то нижча ціна: від 30 шт −5%, від 100 шт −10%', 'Договір і документи з ПДВ']
    tot = ''
    if kids:
        tot = f'''<div class="ftot"><div><small>Наборів</small><b>{money(kids[0])} шт</b></div>
        <div><small>Сума</small><b>{money(kids[1])} грн</b></div></div>'''
    elif totals:
        tot = f'''<div class="ftot"><div><small>За 1 набір</small><b>{money(totals[0])} грн</b></div>
        <div><small>За {QTY} наборів</small><b>{money(totals[1])} грн</b></div></div>'''
    return f'''<div class="foot"><ul class="perks">{''.join(f'<li>{p}</li>' for p in perks)}</ul>{tot}
    <div class="mgr"><small>Ваш персональний ельф</small><b>{m["name"]}</b><span>{m["phone"]} · {m["email"]}</span></div></div>'''

V = []
for i,(name,tag,codes) in enumerate(VARIANTS,1):
    s = sum(price(c) for c in codes); V.append((i,name,tag,codes,s,s*QTY))

# Слайд 1
K_QTY = sum(k[4] for k in KIDS); K_SUM = sum(k[4]*k[5] for k in KIDS)
conds = []
if V:
    conds.append(('Кількість', f'{QTY} наборів'))
    if BUDGET: conds.append(('Бюджет на набір', f'≈ {money(BUDGET)} грн'))
if KIDS: conds.append(('Цукеркові подарунки', f'{money(K_QTY)} шт'))
conds.append(('Ціни', 'з ПДВ'))
conds_html = ''.join(f'<div><small>{a}</small><b>{b}</b></div>' for a,b in conds)
if V and KIDS: lead_html = 'Три варіанти наповнення в межах бюджету та готові цукеркові подарунки.'
elif V: lead_html = 'Три варіанти наповнення в межах вашого бюджету. Усі позиції є на складі в потрібній кількості.'
else: lead_html = 'Готові цукеркові подарунки для дітей ваших співробітників і партнерів. Ціна знижується зі збільшенням кількості.'
kids_chip = ''
cards = ''
for i,name,tag,codes,s,t in V:
    th = ''.join(thumb(c,'mini') for c in codes[:5])
    more = ''
    lst = ''.join(f'<li><span>{I[c][0]}</span><em>{I[c][1]}</em></li>' for c in codes)
    cards += f'''<div class="vcard"><div class="vnum">Варіант {i}</div><h3>{name}</h3><p class="vtag">{tag}</p>
    <div class="minis">{th}{more}</div><ul class="vlist">{lst}</ul><div class="vmeta">{len(codes)} позицій · {storage_line(codes).replace('Зберігання в офісі ','').replace('Зберігати в прохолодному місці, ','')}</div>
    <div class="vprice"><b>{money(s)} грн</b><small>за набір</small></div><div class="vtotal">{money(t)} грн за {QTY} наборів</div></div>'''
if V:
    right_html = f'<div class="vcards">{cards}</div>'
else:
    prev = ''.join(f'<div class="kprev">{thumb(k[0],"mini")}<span>{k[1]}</span><em>{money(k[4])} шт</em></div>' for k in KIDS[:8])
    right_html = f'<div class="kpreview"><h3>Цукеркові подарунки</h3><div class="kprevgrid">{prev}</div><div class="vprice"><b>{money(K_SUM)} грн</b><small>за {money(K_QTY)} наборів</small></div></div>'
slide1 = f'''<div class="slide s1">{SNOW_TITLE}{GARLAND}{BAUBLES}<div class="head">{LOGO}<div class="hr"><b>Комерційна пропозиція</b><span>{KP_DATE}</span></div></div>
<div class="s1body"><div class="s1left"><div class="kicker">Помічники Святого Миколая від Office Better</div>
<h1>{'Товари для ваших новорічних наборів' if V else 'Новорічні цукеркові подарунки'}</h1>
<div class="conds">{conds_html}</div>
<p class="lead">{lead_html}</p>{kids_chip}
<img class="mascot{' mascot-sm' if (V and KIDS) else ''}" src="data:image/png;base64,{mascot}" alt=""></div>
{right_html}</div>{footer()}</div>'''

slides = [slide1]
for i,name,tag,codes,s,t in V:
    cards_html = ''
    for n,c in enumerate(codes,1):
        nm,pack,brand,cat,opt,st,desc,stor,_ = I[c]
        cards_html += f'''<div class="pc"><div class="pcph">{thumb(c,'big')}<span class="pcn">{n}</span></div>
        <div class="pci"><b>{nm}</b><div class="pcm">{pack} · {brand}</div><p>{desc}</p><small>Зберігання: {stor}</small></div>
        <div class="pcp">{money(price(c))}<small>грн</small></div></div>'''
    rowsn = (len(codes)+1)//2
    gap = 3.0; avail = 141.0
    rowh = (avail - gap*(rowsn-1)) / rowsn
    phs = min(34.0, rowh - 4.4)
    slides.append(f'''<div class="slide">{SNOW_SPEC}{GARLAND}<div class="head">{LOGO}<div class="ht"><small>Варіант {i}</small><b>{name}</b><span>{tag}</span></div></div>
<div class="pgrid" style="grid-template-rows: repeat({rowsn}, {rowh:.2f}mm); --ph: {phs:.2f}mm">{cards_html}</div>
{footer(codes,(s,t))}</div>''')

# Сторінки «Цукеркові подарунки» (до 8 наборів на сторінку)
for pg_i in range(0, len(KIDS), 8):
    chunk = KIDS[pg_i:pg_i+8]
    kc = ''
    for code, nm, wt, comp, q, pr in chunk:
        kc += f'''<div class="kc">{thumb(code,'kph')}<div class="kci"><b>{nm}</b><span class="kw">{wt}</span>
        <p>{comp}</p></div><div class="kcp"><span>{money(q)} шт × {money(pr)} грн</span><b>{money(q*pr)} грн</b></div></div>'''
    more = ' (продовження)' if pg_i else ''
    slides.append(f'''<div class="slide">{SNOW_SPEC}{GARLAND}<div class="head">{LOGO}<div class="ht"><small>Додатково</small><b>Цукеркові подарунки{more}</b><span>Готові набори цукерок для дітей ваших співробітників і партнерів</span></div></div>
<div class="kgrid{' k2' if len(chunk) <= 4 else ''}">{kc}</div>
{footer(kids=(K_QTY, K_SUM))}</div>''')

css = open(os.path.join(HERE,'style.css')).read()
html = f'''<!doctype html><html lang="uk"><head><meta charset="utf-8"><title>КП Office Better — товари для новорічних наборів</title>
<style>{fonts}{css}</style></head><body>{''.join(slides)}</body></html>'''
open(os.environ.get('KP_OUT','/mnt/user-data/outputs/KP.html'),'w',encoding='utf-8').write(html)
print('photos used:', sorted(photos), 'size KB', len(html)//1024)
