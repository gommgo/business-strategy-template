#!/usr/bin/env python3
"""loop_rife_bridge.py — RIFE-мост петли: промежуточные кадры от последнего кадра к первому (оптический поток RIFE v4.6,
ncnn/Vulkan), без смешивания двух картинок — кроссфейд даёт «фантом» на крупной форме. Выход — мезонин x264 -qp 0.

  loop_rife_bridge.py IN.mp4 OUT.mp4 [K] [--dry-run]
  loop_rife_bridge.py --selftest

Длина моста K — от шва и движения у концов (метрики video_loop_check.py: шов — MAD последнего и первого кадра, движение
у концов — медиана трёх пар у каждого конца): K = ceil(шов / движение у концов) − 1, шаг моста не больше движения соседних
кадров и больше его половины. Мост длиннее даёт почти неподвижные кадры — приёмка читает их как угасание. У почти
неподвижных концов опора — не ниже «мёртвой» пары (video.dead_pair_frac × медиана движения): шаг моста «мёртвым» не
бывает. Шов в норме мезонина (отношение не больше video.seam_local_max) — мост не нужен: файл не пишется, код 3. K третьим
аргументом задаёт длину вручную; --dry-run — только расчёт, без RIFE. Числа — kb/ai-media/11-evaluation-qa/thresholds.yaml.
Запуск — под замком heavy, при свободной памяти от 3 ГБ; нужен rife-ncnn-vulkan (scripts/install.sh --bin).
Вывод — JSON: шов, движение у концов, длина моста, шаг моста к движению у концов, число кадров.
Код выхода: 0 — мост построен, расчёт --dry-run выполнен, самопроверка прошла; 1 — сбой ffmpeg или RIFE, самопроверка
не прошла; 2 — ошибка вызова или окружения; 3 — мост не нужен."""
import argparse, json, math, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # scripts/lib: kbpaths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbpaths  # noqa: E402

RIFE = kbpaths.bin_dir('rife-ncnn-vulkan', 'rife-ncnn-vulkan')
MODEL = kbpaths.bin_dir('rife-ncnn-vulkan', 'rife-v4.6')


def bridge_len(seam_mad, ends_motion, motion_med, dead, seam_max):
    """Число кадров моста. Опора шага — движение у концов, но не ниже «мёртвой» пары (dead × медиана движения); шов в
    норме мезонина (отношение к опоре не больше seam_max) — мост не нужен (0)."""
    ref = max(ends_motion, dead * motion_med)
    if ref <= 0 or seam_mad / ref <= seam_max:
        return 0
    return max(0, math.ceil(seam_mad / ref) - 1)


def plan(frames, th):
    """Расчёт моста по кадрам: {seam_mad, ends_motion, motion_med, bridge, step_ratio} — шаг моста к движению у концов."""
    import video_loop_check as vl
    m = vl.loop_metrics(frames, th=th)
    k = bridge_len(m['seam_mad'], m['ends_motion'], m['motion_med'], vl.lim(th, 'video.dead_pair_frac'),
                   vl.lim(th, 'video.seam_local_max'))
    ref = max(m['ends_motion'], vl.lim(th, 'video.dead_pair_frac') * m['motion_med'], 1e-6)
    return {'seam_mad': m['seam_mad'], 'ends_motion': m['ends_motion'], 'motion_med': m['motion_med'],
            'seam_ratio_local': m['seam_ratio_local'], 'bridge': k, 'step_ratio': round(m['seam_mad'] / (k + 1) / ref, 2)}


def build(src, out, k):
    """K кадров RIFE между последним и первым кадром, затем мезонин без потерь."""
    tmp = tempfile.mkdtemp(prefix='rife_', dir=os.path.dirname(os.path.abspath(out)))
    try:
        fr = os.path.join(tmp, 'f'); os.makedirs(fr)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vsync', '0', os.path.join(fr, '%05d.png')], check=True)
        frames = sorted(os.listdir(fr)); n = len(frames)
        last, first = os.path.join(fr, frames[-1]), os.path.join(fr, frames[0])
        for i in range(1, k + 1):
            t = i / (k + 1)
            dst = os.path.join(fr, f'{n + i:05d}.png')
            subprocess.run([str(RIFE), '-0', last, '-1', first, '-o', dst, '-s', f'{t:.6f}', '-m', str(MODEL), '-j', '1:1:1'],
                           check=True, capture_output=True)
        fps = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate',
                                         '-of', 'json', src], capture_output=True, text=True).stdout)['streams'][0]['avg_frame_rate']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', fps, '-i', os.path.join(fr, '%05d.png'), '-an', '-c:v', 'libx264',
                        '-qp', '0', '-pix_fmt', 'yuv444p', '-preset', 'medium', '-threads', '4', '-movflags', '+faststart', out], check=True)
        return {'in_frames': n, 'out_frames': n + k, 'fps': fps}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    """Сухой расчёт длины моста на синтетических петлях с известным швом, без RIFE и ffmpeg."""
    import video_loop_check as vl
    th = vl.limits()
    dead, seam_max = vl.lim(th, 'video.dead_pair_frac'), vl.lim(th, 'video.seam_local_max')
    ok = True

    def check(msg, cond, info=''):
        nonlocal ok
        ok = ok and bool(cond)
        print(('OK   ' if cond else 'FAIL ') + msg + (f'  → {info}' if not cond else ''))
    s = vl.synth()
    n = len(s)
    small, big, closed = plan(s[: n - 1], th), plan(s[: n - 3], th), plan(s, th)
    check('малый шов (стык вдвое длиннее шага): мост в один кадр, шаг моста — как у соседних кадров',
          small['bridge'] == 1 and 0.5 < small['step_ratio'] <= 1.05, small)
    check('большой шов (стык в четыре шага): мост в три кадра', big['bridge'] == 3 and 0.5 < big['step_ratio'] <= 1.05, big)
    check('петля замкнута (шов в норме мезонина): мост не нужен', closed['bridge'] == 0
          and bridge_len(seam_max, 1.0, 1.0, dead, seam_max) == 0, closed)
    check('шаг моста не «мёртвый»: больше половины движения у концов и не больше его при любом шве выше нормы',
          all(0.5 < x / (bridge_len(x, 1.0, 1.0, dead, seam_max) + 1) <= 1 for x in (seam_max + 0.1, 2.0, 3.3, 7.9)))
    check('почти неподвижные концы: опора — «мёртвая» пара, а не ноль',
          bridge_len(1.0, 0.0, 1.0, dead, seam_max) == math.ceil(1 / dead) - 1 and bridge_len(1.0, 0.0, 0.0, dead, seam_max) == 0)
    print('loop_rife_bridge selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', metavar='IN'); ap.add_argument('out', metavar='OUT')
    ap.add_argument('k', metavar='K', nargs='?', type=int, help='длина моста вручную; без неё — расчёт по шву и движению у концов')
    ap.add_argument('--dry-run', action='store_true', help='только расчёт длины моста, файл не пишется')
    a = ap.parse_args()
    if not os.path.isfile(a.src):
        print(f'loop_rife_bridge.py: нет файла {a.src}', file=sys.stderr)
        return 2
    import video_loop_check as vl
    try:
        res = plan(vl.load(a.src, 320), vl.limits())
    except vl.ThresholdError as e:
        print(f'loop_rife_bridge.py: {e}', file=sys.stderr)
        return 2
    if a.k is not None:
        if a.k < 0:
            print('loop_rife_bridge.py: K — целое число не меньше нуля', file=sys.stderr)
            return 2
        res.update(bridge=a.k, manual=True)
    if a.dry_run or not res['bridge']:
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res['bridge'] or a.dry_run else 3
    if not RIFE.exists():
        print(f'loop_rife_bridge.py: нет {RIFE} — поставьте scripts/install.sh --bin', file=sys.stderr)
        return 2
    try:
        res.update(build(a.src, a.out, res['bridge']))
    except subprocess.CalledProcessError as e:
        print(f'loop_rife_bridge.py: сбой {os.path.basename(str(e.cmd[0]))} (код {e.returncode})', file=sys.stderr)
        return 1
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
