
import os

files_to_check = [
    r'apps\admin\views.py',
    r'apps\admin\urls.py',
]

for relative_path in files_to_check:
    file_path = os.path.join(os.getcwd(), relative_path)
    if os.path.exists(file_path):
        print(f"Checking {file_path}...")
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            if b'\x00' in content:
                print(f"Null bytes found in {file_path}. cleaning...")
                new_content = content.replace(b'\x00', b'')
                with open(file_path, 'wb') as f:
                    f.write(new_content)
                print("Cleaned.")
            else:
                print("No null bytes found.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")
