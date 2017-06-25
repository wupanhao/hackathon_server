import os
import subprocess
import json
import mysql.connector as mariadb
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import time
from numpy import array
import numpy  as np
array = np.array
float32 = np.float32

mariadb_connection = mariadb.connect(user='root', password='', database='class_monitor')
cursor = mariadb_connection.cursor()

# import base64

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
        course_id = request.form.get('id')
        date = request.form.get('date')
        print(fname)
        new_filename = fname

        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        img_url = "http://43.241.238.58:5000/static/upload/%s" % fname


        cursor.execute("insert into imgs values('%s','%s','%s')" % (course_id,date,img_url))
        mariadb_connection.commit()

        token = new_filename

        return jsonify({"errno": 0, "errmsg": "上传成功", "token": token})

    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})


@app.route('/api/speech', methods=['POST'])
def upload_speech():
    course_id = request.form.get('id')
    date = request.form.get('date')
    text = request.form.get('text')
    sql = "insert into text values (%d,'%s', '%s')" % (int(course_id), date, text)
    print(sql)
    cursor.execute(sql)
    mariadb_connection.commit()
    return jsonify('Uploaded successfully')

@app.route('/api/process', methods=['GET','POST'])
def process():
    course_id = request.form.get('id')
    sql = "select * from imgs where course_id=%s" % (course_id)
    print(sql)
    cursor.execute(sql)
    for i in cursor:
        img_url = i[2].decode('utf-8')
        cmd = 'python Face/face.py  "%s"' % img_url
        result_str = subprocess.check_output(cmd,shell=True)
        result_list = eval(result_str)
        for name, attention in result_list:
            sql = "insert into attention values('%s','%s','%s','%s') " % (course_id, name, date, attention)
            print(sql)
            cursor.execute(sql)
            mariadb_connection.commit()
        print(img_url)
    return "OK"


@app.route('/api/result', methods=['GET'])
def finish():
    course_id = request.form.get('id')
    sql = "select name,time,attention from attention inner_join users on attention.user_id=users.face_id  where course_id='%s'" % (course_id)
    print(sql)
    cursor.execute(sql)
    r = []
    for i in cursor:
        r.append(i)
    return json.dumps(r)

@app.route('/test', methods=['GET'])
def test():
    a = [('yyf', 0.5), ('wph', 1)]
    course_id = request.form.get('id')
    date = request.form.get('date')
    for name, attention in a:
        sql = "insert into attention values('%s','%s','%s','%s') " % (course_id, name, date, attention)
        print(sql)
        cursor.execute(sql)
        mariadb_connection.commit()
    return jsonify({"errno": 0, "errmsg": "success"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)