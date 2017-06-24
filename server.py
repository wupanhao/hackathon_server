'''
import mysql.connector as mariadb
mariadb_connection = mariadb.connect(user='python_user', password='some_pass', database='employees')
cursor = mariadb_connection.cursor()
'''
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import time
import os
import base64
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传，稍后用到
@app.route('/test/upload')
def upload_test():
    return render_template('upload.html')


# 上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '.' + ext  # 修改了上传的文件名
        new_filename = fname
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        token = new_filename
        # token = base64.b64encode(new_filename)
        print(token)
        img_url = "http://43.241.238.58:5000/static/upload/%s" % fname
        cmd = 'python face.py  "%s"' % img_url
        print(img_url)
        a=[('yyf',0.5),('wph',1)]
        # a = subprocess.check_output(cmd,shell=True)
        # print(a)
        id = request.form.get('id')
        date = request.form.get('date')
        for name,attention in a:
            sql = "insert into attention values('%s','%s','%s','%s') " % (id,name,time,attention)
            print(sql)
        return jsonify({"errno": 0, "errmsg": "上传成功", "token": token})
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})

@app.route('/api/speech',methods=['POST'])
def upload_speech():
    date = request.form.get('date')
    text = request.form.get('text')
    sql = "insert into text values ('%s','%s')" % (date,text.encode('utf-8'))
    print(sql)
    return sql

@app.route('/api/finish',methods=['GET'])
def finish():
    id = request.form.get('id')
    sql = "select * from courses where id='%s'" % (id)
    print(sql)
    return sql

@app.route('/test',methods=['GET'])
def test():
    a = [('yyf', 0.5), ('wph', 1)]
    id = request.form.get('id')
    date = request.form.get('date')
    for name, attention in a:
        sql = "insert into attention values('%s','%s','%s','%s') " % (id, name, date, attention)
        print(sql)
    return jsonify({"errno": 0, "errmsg": "success"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)