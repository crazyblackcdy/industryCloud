import time
import os
import json
import shutil
from copy import deepcopy
from flask import Flask, request, render_template, make_response, Response, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from dicts_and_set import *
from icecream import ic

"""Flask"""
app = Flask(__name__, template_folder='templates', static_folder='static')
# filename = []

# 设置连接的数据库uri
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://quickml:quickml@localhost:3306/quick_ml"
# 设置每次请求结束后，会自动提交数据库的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 查询时显示原始sql语句
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)

CORS(app)

"""Database"""


# 数据库存储各种训练模型表：modules
class Modules(db.Model):
    # 定义表名
    __tablename__ = 'modules'
    MODULEID = db.Column(db.Integer, primary_key=True)  # 101
    TYPE = db.Column(db.Integer, unique=False)  # 1
    TYPENAME = db.Column(db.String(32), unique=False)  # 分类
    NAME = db.Column(db.String(64), unique=False)  # GaussianNB
    IMPORTING = db.Column(db.String(128), unique=False)  # from…………import…………

    def __repr__(self):
        return '<module: %s\t%s\t%s\t%s\t%s>' % (self.TYPE, self.TYPENAME, self.MODULEID, self.NAME, self.IMPORTING)


# 数据库账户表：accounts
class Accounts(db.Model):
    __tablename__ = 'accounts'
    USERNAME = db.Column(db.String(32), primary_key=True)  # 用户名，作为主键，不可重复
    PASSWORD = db.Column(db.String(32), unique=False)  # 用户密码
    EMAIL = db.Column(db.String(128), unique=False)  # 用户邮箱

    def __repr__(self):
        return '<account: %s\t%s\t%s>' % (self.USERNAME, self.PASSWORD, self.EMAIL)


# 数据库训练项目表：trains
class Trains(db.Model):
    __tablename__ = 'trains'
    TRAINID = db.Column(db.Integer, primary_key=True)  # 唯一的训练ID（应注意用户和开始训练的时间相结合产生的唯一性）
    USERNAME = db.Column(db.String(32), db.ForeignKey(Accounts.USERNAME), unique=False)  # 提交此训练的用户
    TRAINFILES = db.Column(db.String(256), unique=False)  # 保存训练上传的文件所在地址，文件之间用‘;’隔开
    USEPCA = db.Column(db.Boolean, unique=True)  # 是否降维
    STARTTIME = db.Column(db.DateTime, unique=False)  # 开始训练时间（点击按钮）
    TRAINFINISHED = db.Column(db.Boolean, unique=False, default=False)  # 是否已经完成训练，默认未完成

    def __repr__(self):
        return '<train: %s\t%s\t%s\t%s>' % (self.TRAINID, self.USERNAME, self.STARTTIME, self.TRAINFINISHED)


# 数据库具体结果表：results
class Results(db.Model):
    __tablename__ = 'results'
    SPECIFICID = db.Column(db.Integer, primary_key=True)  # 具体训练结果的ID
    TRAINID = db.Column(db.Integer, db.ForeignKey(Trains.TRAINID), unique=False)  # 对应外键trainID，用于查找此训练的所有结果
    MODULEID = db.Column(db.Integer, db.ForeignKey(Modules.MODULEID), unique=False)  # 对应外键moduleID
    # modulename = db.Column(db.String(64), unique=False)  # module名
    # RUNNINGTIME = db.Column(db.Float(precision="6,6"), unique=False)  # 运行时间，需要确认是否能正确显示
    # ACCURACY = db.Column(db.Float(precision="6,3"), unique=False)  # 正确率，输出需要在后面加%
    RUNNINGTIME = db.Column(db.String(8), unique=False)  # 运行时间，需要确认是否能正确显示
    ACCURACY = db.Column(db.String(8), unique=False)  # 正确率，输出需要在后面加%
    IMGPATH_CONFUSION = db.Column(db.String(64), unique=False)  # 混淆矩阵图片存放位置
    FINISHED = db.Column(db.Boolean, default=False)  # 具体训练是否完成

    def __repr__(self):
        return '<result: %s\t%s\t%s\t%s\t%s\t%s\t%s>' % \
               (self.SPECIFICID, self.TRAINID, self.MODULEID, self.RUNNINGTIME,
                self.ACCURACY, self.IMGPATH_CONFUSION, self.FINISHED)


# 初始化数据库表
def init_db():
    db.session.commit()
    db.session.remove()
    db.drop_all()  # 删除所有表
    db.create_all()  # 创建所有表

    modules = []
    for Mk, Mvs in MODEL_DICT.items():
        if type(Mvs) == str:
            mtype = 4
            m = Modules(MODULEID=Mk, TYPE=mtype, TYPENAME=Typename[mtype - 1],
                        NAME=Mvs.split('.')[0][5:], IMPORTING=Mvs.split('.')[0][5:])
            modules.append(m)
            continue
        for k, v in Mvs.items():
            m = Modules(MODULEID=k, TYPE=Mk, TYPENAME=Typename[int(Mk) - 1], NAME=v.split(' ')[-1], IMPORTING=v)
            modules.append(m)
    db.session.add_all(modules)

    a = Accounts(USERNAME='superadmin', PASSWORD='666', EMAIL='666@jnu.com')
    b = Accounts(USERNAME='ZhangSan', PASSWORD='666', EMAIL='666@jnu.com')

    db.session.add(a)
    db.session.add(b)

    db.session.commit()


init_db()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        pass
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        a = Accounts.query.filter_by(USERNAME=username).all()

        if a[0].PASSWORD != password:
            print('密码错误')
            coo = Response()
            coo.set_cookie('status', '0')
            # res = json.dumps({'status': 0, 'msg': '密码错误'})
            return coo
        elif a[0].PASSWORD == password:
            print(username, "登录成功")
        else:
            a = Accounts(USERNAME=username, PASSWORD=password)
            print("创建用户成功：", username)
            db.session.add(a)
            db.session.commit()

        # coo = make_response("success")
        coo = Response()
        coo.set_cookie('status', '1')
        coo.set_cookie("user", str(username))
        coo.set_cookie("trainid", '0')
        ic(coo)
        return coo


@app.route('/<name>')
def user(name):
    if name == 'model_select.html':
        Ms = Modules.query.all()
        ic(Ms)
        return render_template(name, Ms=Ms)
    else:
        return render_template(name)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        pass
    else:
        username = request.cookies.get('user')
        trainid = int(request.cookies.get('trainid'))  # 默认值为0
        # starttime = request.cookies.get('starttime')
        ic(username, trainid)

        file = request.files.get('file')

        # 数据库训练项目表操作
        if trainid == 0:
            t = Trains.query.order_by(Trains.TRAINID.desc()).first()
            ic(t)
            if t is None:
                trainid = 1
            else:
                trainid = t.TRAINID + 1

            file_dir = os.path.join('./Datasets/', str(trainid))
            if not os.path.exists(file_dir):
                os.mkdir(file_dir)

            filepath = os.path.join('./Datasets/' + str(trainid) + '/', file.filename)
            file.save(filepath)
            t = Trains(TRAINID=trainid, USERNAME=username, TRAINFILES=filepath)
            ic('新建train', t)
            db.session.add(t)
            db.session.commit()

            coo = Response()
            coo.set_cookie('trainid', str(trainid))
            return coo

        else:
            filepath = os.path.join('./Datasets/' + str(trainid) + '/', file.filename)
            file.save(filepath)
            t = Trains.query.filter_by(USERNAME=username, TRAINID=trainid).all()[0]
            f = deepcopy(t.TRAINFILES).split(';')
            if filepath not in f:
                t.TRAINFILES += (';' + filepath)
                ic('后续文件', t)
            else:
                ic('文件重复上传')
            db.session.commit()
            return 'Upload ' + file.filename + ' Done'


@app.route('/runmodel', methods=['GET', 'POST'])
def test():
    if request.method == 'GET':
        pass
    else:
        rs = []  # result表待加入的数据

        trainid = int(request.cookies.get('trainid'))
        models_arg1 = request.get_data()
        models_arg = str(models_arg1)[2:-1].split('&')[:-1]
        # pca = request.form.get("pca")
        # pca = True if pca.lower() == 'true' else False
        # ic(models_arg1, models_arg, pca)

        result_path = './static/modelresult/' + str(trainid)
        if os.path.exists(result_path):
            shutil.rmtree(result_path)
        os.mkdir(result_path)

        for models in models_arg:
            moduleid = int(models.split('=')[-1])

            if moduleid is None:
                return 'Please choose a model!'

            specificid = moduleid + trainid * 10 ** len(str(moduleid))
            r = Results(SPECIFICID=specificid, TRAINID=trainid, MODULEID=moduleid)
            rs.append(r)
        ic(rs)
        db.session.add_all(rs)
        db.session.commit()

        # 查询与修改trainid条目
        t = Trains.query.filter_by(TRAINID=trainid)[0]
        # t.USEPCA = pca
        trainfiles = t.TRAINFILES.split(';')
        if trainfiles is None:
            return 'Please upload a file first!'


        for r in rs:
            module = Modules.query.filter_by(MODULEID=r.MODULEID)[0]
            type = module.TYPE
            name = module.MODULEID
            # ic(trainid, r.SPECIFICID, trainfiles, 'target', 'features', type, name, result_path)
            myModel = SetModel(trainid, r.SPECIFICID, trainfiles, 'target', 'features', type, name, result_path)
            myModel.get_code()
            os.system('python generate.py')
            with open('./static/modelresult/'+str(trainid)+'/result.txt', 'r') as f:
                _train_result = f.read().split('*')
            r.RUNNINGTIME, r.ACCURACY, r.IMGPATH_CONFUSION, F = _train_result
            r.FINISHED = True if F == "True" else False
            ic(r)
            db.session.commit()
        ic(rs)

        # 所有具体训练完成，修改训练项目表的finished
        t = Trains.query.filter_by(TRAINID=trainid).all()
        if len(t) != 1:
            print("trainid is not unique, please check the database")
        t[0].TRAINFINISHED = True

        db.session.commit()
        return 'Congratulations Model Done'
        # return


@app.route('/getSelectedModels', methods=['GET'])
def getSelectedModels():
    trainid = int(request.cookies.get('trainid'))
    rs = Results.query.filter_by(TRAINID=trainid).all()
    sel_models = []
    for r in rs:
        sel_model = Modules.query.filter(Modules.MODULEID == r.MODULEID)[0]
        sel_model = sel_model.NAME
        sel_models.append(sel_model)
    data = {'Models': sel_models}
    res = json.dumps(data)
    ic(res)
    return res


@app.route('/getTrainedResult', methods=['GET'])
def getTrainedResult():
    trainid = int(request.cookies.get('trainid'))
    t = Trains.query.filter_by(TRAINID=trainid).all()
    assert len(t) == 1
    t = t[0]

    data = {'TrainedResult': [], 'Finished': t.TRAINFINISHED}
    out = Results.query.filter(Results.TRAINID == t.TRAINID).all()
    ic(out)
    # assert len(rs) > 0
    for R in out:
        if R.FINISHED:
            modulename = Modules.query.filter(Modules.MODULEID == R.MODULEID)[0].NAME
            tem = [modulename, str(R.RUNNINGTIME) + 's', str(R.ACCURACY) + '%', R.IMGPATH_CONFUSION]
            data['TrainedResult'].append(tem)
    ic(data)

    res = json.dumps(data)
    if t.TRAINFINISHED:
        coo = Response(res)
        coo.delete_cookie('trainid', str(trainid))
        coo.set_cookie('trainid', '0')
        return coo
    return res


@app.errorhandler(403)
def page_not_found(e):
    return render_template("404.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(405)
def page_not_found(e):
    return render_template("404.html"), 405


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


@app.errorhandler(503)
def page_not_found(e):
    return render_template("404.html"), 503


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050)

# For the test
# myModel = SetModel(['flex.csv','punch.csv'], 'target', 'features', '1', 'decisiontree', ['ROCcurve','confusion'])
# myModel.get_code()
# import generate
