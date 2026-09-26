# RIFE-мост петли: k промежуточных кадров от последнего кадра к первому (оптический поток RIFE v4.6, ncnn/Vulkan), без
# смешивания двух картинок (кроссфейд давал «фантом» на крупной форме — голос заказчика 25.09). Выход — мезонин x264 -qp 0.
# Запуск (под heavy.lock, при free ≥ 3 ГБ): python3 loop_rife_bridge.py IN.mp4 OUT.mp4 [k=8]
import json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
RIFE = str(kbpaths.bin_dir('rife-ncnn-vulkan', 'rife-ncnn-vulkan'))
MODEL = str(kbpaths.bin_dir('rife-ncnn-vulkan', 'rife-v4.6'))
src, out = sys.argv[1], sys.argv[2]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 8
tmp = tempfile.mkdtemp(prefix='rife_', dir=os.path.dirname(os.path.abspath(out)))
try:
    fr = os.path.join(tmp, 'f'); os.makedirs(fr)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vsync', '0', os.path.join(fr, '%05d.png')], check=True)
    frames = sorted(os.listdir(fr)); n = len(frames)
    last, first = os.path.join(fr, frames[-1]), os.path.join(fr, frames[0])
    for i in range(1, k + 1):
        t = i / (k + 1)
        dst = os.path.join(fr, f'{n + i:05d}.png')
        subprocess.run([RIFE, '-0', last, '-1', first, '-o', dst, '-s', f'{t:.6f}', '-m', MODEL, '-j', '1:1:1'],
                       check=True, capture_output=True)
    fps = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate',
                                     '-of', 'json', src], capture_output=True, text=True).stdout)['streams'][0]['avg_frame_rate']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', fps, '-i', os.path.join(fr, '%05d.png'), '-an', '-c:v', 'libx264',
                    '-qp', '0', '-pix_fmt', 'yuv444p', '-preset', 'medium', '-threads', '4', '-movflags', '+faststart', out], check=True)
    print(json.dumps({'in_frames': n, 'bridge': k, 'out_frames': n + k, 'fps': fps}))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
