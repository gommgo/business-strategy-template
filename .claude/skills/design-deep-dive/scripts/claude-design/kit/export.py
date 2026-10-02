#!/usr/bin/env python3
"""kit/export.py — экспорт холста без интерфейса Claude Design: PDF по артбордам, PNG 2×, standalone.html, zip.

Холст — рамки манифеста: `kit.json` статичных копий артбордов или `canvas.json` kit; рамка — копия на ширине своей
рамки, standalone раскладывает их рядами по ширинам (`canvas.html`). Манифест читается как при съёмке (`shot.py`):
`--manifest kit.json` без такого файла в папке копий — манифест считается из статичных копий (подписи и порядок — из
исходников холста, ключ --canvas). Использует сервер, блокировку и проверку памяти из shot.py (тот же каталог).

Использование:
  python3 export.py <pdf|png2x|standalone|zip|all> <папка проекта> <outdir> [--manifest canvas.json] [--only landing.html]
          [--canvas ПАПКА] [--lock /path/to/browser.lock] [--min-free-gb 2]
Что получается:
  pdf        <файл>-<W>-<тема>.pdf — артборд одной страницей во всю высоту (вектор: текст выделяется, шрифты встроены),
             плюс canvas.pdf — все рамки подряд (pypdf). Экранные стили (emulate_media screen), фоны печатаются.
  png2x      <файл>-<W>-<тема>@2x.png — артборд целиком при DPR 2, без меток.
  standalone standalone.html — весь холст одним файлом: манифест, артборды (CSS, картинки и шрифты-файлы вложены, Google
             Fonts — ссылкой), marks.js. Открывается двойным щелчком (file://), метки: ?marks=1. Предупреждает, если > 16 МиБ
             (предел страницы артефакта Claude Code).
  zip        <название>.zip — исходники проекта (HTML, CSS, JS, JSON, SVG, картинки, шрифты, DESIGN.md) + всё, что уже лежит в
             outdir (standalone.html, PDF, PNG 2×).
  all        standalone → pdf → png2x → zip.
Браузер нужен только pdf и png2x.
"""
import argparse, base64, json, mimetypes, os, re, sys, time, zipfile

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT_DIR)
import shot  # noqa: E402  (serve, BrowserLock, mem_available_gb, slug)

KEEP_EXT = {'.html', '.htm', '.css', '.js', '.mjs', '.json', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif',
            '.woff', '.woff2', '.ttf', '.otf', '.md', '.txt', '.mp4', '.webm'}
PAGE_LIMIT = 16 * 1024 * 1024


def frames_of(manifest, only):
    out = []
    for ab in manifest.get('artboards', []):
        if only and ab['file'] not in only:
            continue
        out.append({**ab, 'theme': ab.get('theme', 'light')})
    return out


def stem_of(fr):
    return f"{shot.slug(os.path.splitext(fr['file'])[0])}-{int(fr['w'])}-{fr['theme']}"


def open_page(browser, base_url, fr, dpr):
    w, h = int(fr['w']), int(fr['h'])
    scheme = fr['theme'] if fr['theme'] in ('light', 'dark') else None
    ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, is_mobile=w < 768,
                              has_touch=w < 1024, reduced_motion='reduce', color_scheme=scheme)
    page = ctx.new_page()
    page.goto(f"{base_url}/{fr['file']}", wait_until='networkidle', timeout=60000)
    page.evaluate('document.fonts ? document.fonts.ready.then(() => true) : true')
    if scheme:
        page.evaluate("(t) => { document.documentElement.setAttribute('data-theme', t); document.documentElement.style.colorScheme = t; }", scheme)
    page.wait_for_timeout(300)
    return ctx, page


def do_pdf(project, outdir, manifest, only, browser, base_url, report):
    from pypdf import PdfWriter, PdfReader
    paths = []
    for fr in frames_of(manifest, only):
        ctx, page = open_page(browser, base_url, fr, 1)
        page.emulate_media(media='screen', reduced_motion='reduce')
        height = page.evaluate('Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
        path = os.path.join(outdir, stem_of(fr) + '.pdf')
        page.pdf(path=path, width=f"{int(fr['w'])}px", height=f'{int(height) + 2}px', print_background=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, page_ranges='1')
        ctx.close()
        pages = len(PdfReader(path).pages)
        report['pdf'].append({'frame': f"{fr['file']}@{fr['w']}@{fr['theme']}", 'path': path, 'pages': pages,
                              'css_px': [int(fr['w']), int(height)], 'bytes': os.path.getsize(path)})
        paths.append(path)
    if paths:
        wr = PdfWriter()
        for pth in paths:
            for pg in PdfReader(pth).pages:
                wr.add_page(pg)
        cpath = os.path.join(outdir, 'canvas.pdf')
        with open(cpath, 'wb') as fh:
            wr.write(fh)
        report['canvas_pdf'] = {'path': cpath, 'pages': len(paths), 'bytes': os.path.getsize(cpath)}


def do_png2x(project, outdir, manifest, only, browser, base_url, report):
    for fr in frames_of(manifest, only):
        ctx, page = open_page(browser, base_url, fr, 2)
        path = os.path.join(outdir, stem_of(fr) + '@2x.png')
        page.screenshot(path=path, full_page=True)
        ctx.close()
        from PIL import Image
        with Image.open(path) as im:
            size = im.size
        report['png2x'].append({'frame': f"{fr['file']}@{fr['w']}@{fr['theme']}", 'path': path, 'px': list(size),
                                'bytes': os.path.getsize(path)})


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return f"data:{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode('ascii')}"


def is_local(ref):
    return ref and not re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', ref, re.I)


def inline_css(css, css_dir, project):
    def rep(m):
        ref = m.group(2)
        if not is_local(ref):
            return m.group(0)
        p = os.path.normpath(os.path.join(css_dir, ref.split('?')[0].split('#')[0]))
        if p.startswith(project) and os.path.isfile(p):
            return f'url("{data_uri(p)}")'
        return m.group(0)
    return re.sub(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', rep, css)


def inline_html(path, project):
    html = open(path, encoding='utf-8').read()
    hdir = os.path.dirname(path)

    def link(m):
        tag = m.group(0)
        if not re.search(r'rel\s*=\s*["\']?stylesheet', tag, re.I):
            return tag
        href = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        if not href or not is_local(href.group(1)):
            return tag
        p = os.path.normpath(os.path.join(hdir, href.group(1)))
        if not (p.startswith(project) and os.path.isfile(p)):
            return tag
        css = inline_css(open(p, encoding='utf-8').read(), os.path.dirname(p), project)
        return f'<style data-from="{os.path.relpath(p, project)}">\n{css}\n</style>'

    def src(m):
        attr, q, ref = m.group(1), m.group(2), m.group(3)
        if not is_local(ref):
            return m.group(0)
        p = os.path.normpath(os.path.join(hdir, ref))
        if p.startswith(project) and os.path.isfile(p) and not p.endswith(('.html', '.htm')):
            return f'{attr}={q}{data_uri(p)}{q}'
        return m.group(0)

    def script(m):
        ref = m.group(1)
        if not is_local(ref):
            return m.group(0)
        p = os.path.normpath(os.path.join(hdir, ref))
        if p.startswith(project) and os.path.isfile(p):
            return '<script>\n' + open(p, encoding='utf-8').read().replace('</script', '<\\/script') + '\n</script>'
        return m.group(0)

    html = re.sub(r'<link\b[^>]*>', link, html, flags=re.I)
    html = re.sub(r'<script\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\'][^>]*>\s*</script>', script, html, flags=re.I)
    html = re.sub(r'\b(src|poster)\s*=\s*(["\'])([^"\']+)\2', src, html, flags=re.I)
    html = re.sub(r'style\s*=\s*"([^"]*url\([^"]*)"', lambda m: 'style="' + inline_css(m.group(1), hdir, project) + '"', html)
    return html


def do_standalone(project, outdir, manifest, only, report):
    files = {}
    for fr in frames_of(manifest, only):
        if fr['file'] not in files:
            files[fr['file']] = inline_html(os.path.join(project, fr['file']), project)
    payload = {'manifest': manifest, 'files': files, 'marksSource': open(os.path.join(KIT_DIR, 'marks.js'), encoding='utf-8').read()}
    blob = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
    canvas = open(os.path.join(KIT_DIR, 'canvas.html'), encoding='utf-8').read()
    point = '<!-- kit:embed-point (export.py standalone вставляет сюда манифест, файлы артбордов и marks.js) -->'
    if point not in canvas:
        raise SystemExit('canvas.html: нет точки вставки kit:embed-point')
    canvas = canvas.replace(point, '<script>window.__KIT_STANDALONE__ = ' + blob + ';</script>')
    title = manifest.get('title') or 'Холст'
    canvas = canvas.replace('<title>Холст макета</title>', f'<title>{title}</title>')
    path = os.path.join(outdir, 'standalone.html')
    open(path, 'w', encoding='utf-8').write(canvas)
    size = os.path.getsize(path)
    report['standalone'] = {'path': path, 'bytes': size, 'artboard_files': list(files), 'over_artifact_limit': size > PAGE_LIMIT}


def do_zip(project, outdir, manifest, report):
    name = shot.slug(manifest.get('title') or os.path.basename(project)) or 'design'
    path = os.path.join(outdir, name + '.zip')
    out_abs = os.path.abspath(outdir)
    added = []
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, fs in os.walk(project):
            dirs[:] = [d for d in dirs if not d.startswith('.') and os.path.abspath(os.path.join(root, d)) != out_abs
                       and not d.startswith(('review', 'export', 'node_modules'))]
            for f in sorted(fs):
                p = os.path.join(root, f)
                if os.path.splitext(f)[1].lower() in KEEP_EXT:
                    arc = os.path.join('source', os.path.relpath(p, project))
                    z.write(p, arc); added.append(arc)
        for f in sorted(os.listdir(outdir)):
            p = os.path.join(outdir, f)
            if os.path.isfile(p) and not f.endswith('.zip') and (f == 'standalone.html' or f.endswith(('.pdf', '@2x.png'))):
                arc = os.path.join('export', f)
                z.write(p, arc); added.append(arc)
    report['zip'] = {'path': path, 'bytes': os.path.getsize(path), 'entries': added}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('what', choices=['pdf', 'png2x', 'standalone', 'zip', 'all'])
    ap.add_argument('project'); ap.add_argument('outdir')
    ap.add_argument('--manifest', default='canvas.json')
    ap.add_argument('--canvas', default='', help='папка исходников холста с canvas.json — для манифеста копий, который считается')
    ap.add_argument('--only', default='')
    ap.add_argument('--lock', default=os.environ.get('KIT_BROWSER_LOCK', ''))
    ap.add_argument('--min-free-gb', type=float, default=float(os.environ.get('KIT_MIN_FREE_GB', '0') or 0))
    a = ap.parse_args()
    project = os.path.abspath(a.project)
    manifest = shot.read_manifest(project, a.manifest, a.canvas)[0]
    only = [x.strip() for x in a.only.split(',') if x.strip()]
    os.makedirs(a.outdir, exist_ok=True)
    outdir = os.path.abspath(a.outdir)
    report = {'tool': 'kit/export.py', 'version': '1', 'what': a.what, 'pdf': [], 'png2x': []}
    t0 = time.time()
    steps = ['standalone', 'pdf', 'png2x', 'zip'] if a.what == 'all' else [a.what]
    if 'standalone' in steps:
        do_standalone(project, outdir, manifest, only, report)
    if any(s in steps for s in ('pdf', 'png2x')):
        if a.min_free_gb:
            gb = shot.mem_available_gb()
            if gb is not None and gb < a.min_free_gb:
                print(json.dumps({'error': f'мало памяти: {gb:.1f} ГБ < {a.min_free_gb} ГБ'}, ensure_ascii=False), file=sys.stderr)
                return 2
        from playwright.sync_api import sync_playwright
        httpd, base_url = shot.serve(project)
        try:
            with shot.BrowserLock(a.lock), sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    if 'pdf' in steps:
                        do_pdf(project, outdir, manifest, only, browser, base_url, report)
                    if 'png2x' in steps:
                        do_png2x(project, outdir, manifest, only, browser, base_url, report)
                finally:
                    browser.close()
        finally:
            httpd.shutdown(); httpd.server_close()
    if 'zip' in steps:
        do_zip(project, outdir, manifest, report)
    report['seconds'] = round(time.time() - t0, 1)
    json.dump(report, open(os.path.join(outdir, 'export.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
