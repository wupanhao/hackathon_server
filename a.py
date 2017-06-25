import subprocess
cmd = 'python Face/face.py  "http://43.241.238.58:5000/static/upload/IMG_201706251249208186.jpg"'
a = subprocess.check_output(cmd, shell=True)
print(a)
