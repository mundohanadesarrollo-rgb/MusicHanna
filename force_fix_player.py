import os

file_path = r'c:\Users\DESARROLLO\Desktop\Proyectos\MusicHanna\templates\includes\player.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
new_lines.append('{% load static %}\n')
new_lines.append('<footer class="fixed bottom-0 left-0 right-0 h-24 bg-[rgb(106,4,15)] border-t border-[#9D0208] p-4 z-60" aria-label="Player" {% if sede %}data-sede-id="{{ sede.id }}" data-sid="{{ sede.id }}"{% elif sede_id %}data-sede-id="{{ sede_id }}" data-sid="{{ sede_id }}"{% endif %} data-user-id="{{ request.user.id }}" data-status-url="{% url \'update_sede_status\' %}">\n')
new_lines.append('  <script>window.currentSedeId = "{% if sede %}{{ sede.id }}{% elif sede_id %}{{ sede_id }}{% endif %}";</script>\n')

# Find where the old header ends. It was lines 1 to 18 approx.
# We want to keep from <div class="flex items-center...
started = False
for line in lines:
    if '<div' in line and 'flex items-center justify-between' in line:
        started = True
    if started:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("File player.html successfully rewritten with single-line footer.")
