from pathlib import Path
try:
    from mutagen.mp3 import MP3
except Exception:
    MP3 = None

p = Path('media/canciones/descent-whoosh-long-cinematic-sound-effect-405921.mp3')
print('path ->', p.resolve())
print('exists ->', p.exists())
if p.exists():
    print('size bytes ->', p.stat().st_size)
    if MP3:
        try:
            audio = MP3(p)
            print('mutagen duration secs ->', audio.info.length)
        except Exception as e:
            print('mutagen error ->', e)
    else:
        print('mutagen not installed in venv')
else:
    print('File not found')
