import os

file_path = "../2-side-communication/client.py"
parts = file_path.replace("\\", "/").split("/")

# Add .html to the last part (the file name)
if not parts[-1].endswith(".html"):
    parts[-1] += ".html"

if not parts[-1].endswith(".html"):
    parts[-1] += ".html"

base_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(base_dir, "resources")
abs_path = os.path.join(resources_dir, *parts)

print("Looking for:", abs_path)
print("Base dir:", base_dir)
print(os.path.abspath(abs_path))
