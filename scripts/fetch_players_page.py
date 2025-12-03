import requests
url='http://127.0.0.1:8000/admin/players/'
r=requests.get(url, timeout=5)
print('Status', r.status_code)
text = r.text
start = text.find('const songsData =')
if start!=-1:
    snippet = text[start: start+400]
    print(snippet)
else:
    print('songsData not found')
# find audio player src in included player.html
if 'id="audio-player"' in text:
    idx = text.find('id="audio-player"')
    sub = text[idx: idx+200]
    print('\nAudio element snippet:\n', sub)
