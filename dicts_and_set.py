import os

"""
MODEL_DICT = {
    '分类': {
        '朴素贝叶斯': 'from sklearn.naive_bayes import GaussianNB',
        '决策树': 'from sklearn.tree import DecisionTreeClassifier',
        '支持向量机': 'from sklearn.svm import SVC',
        '神经网络': 'from sklearn.neural_network import MLPClassifier'
    },
    '回归': {
        '线性回归': 'from sklearn.linear_model import LinearRegression',
        '逻辑回归': 'from sklearn.linear_model import LogisticRegression',
        '决策树': 'from sklearn.tree import DecisionTreeRegressor',
        '支持向量机': 'from sklearn.svm import SVR',
        '神经网络': 'from sklearn.neural_network import MLPRegressor'
    },
    '聚类': {
        'K-means': 'from sklearn.cluster import KMeans'
    },
    'ROC曲线': 'plot_ROC_curve.py',
    '混淆矩阵': 'plot_confusion_matrix.py'
}
"""

MODEL_DICT_name = {
    '1': {
        '101': 'GaussianNB',
        '102': 'DecisionTreeClassifier',
        '103': 'SVM',
        '104': 'MLPClassifier'
    },
    '2': {
        '201': 'LinearRegression',
        '202': 'LogisticRegression',
        '203': 'DecisionTreeRegressor',
        '204': 'SVM',
        '205': 'MLPRegressor'
    },
    '3': {
        '301': 'K-Means'
    },
    # '401': 'plot_ROC_curve.py',
    # '402': 'plot_confusion_matrix.py'
}

MODEL_DICT = {
    '1': {
        '101': 'from sklearn.naive_bayes import GaussianNB',
        '102': 'from sklearn.tree import DecisionTreeClassifier',
        '103': 'from sklearn.svm import SVC',
        '104': 'from sklearn.neural_network import MLPClassifier'
    },
    '2': {
        '201': 'from sklearn.linear_model import LinearRegression',
        '202': 'from sklearn.linear_model import LogisticRegression',
        '203': 'from sklearn.tree import DecisionTreeRegressor',
        '204': 'from sklearn.svm import SVR',
        '205': 'from sklearn.neural_network import MLPRegressor'
    },
    '3': {
        '301': 'from sklearn.cluster import KMeans'
    },
    # '401': 'plot_ROC_curve.py',
    # '402': 'plot_confusion_matrix.py'
}

# Typename = ['分类', '回归', '聚类', '评价方法']
Typename = ['分类', '回归', '聚类']


class SetModel():
    """

    用于与前端界面交互，获取特征列，以及数据处理步骤。
    根据用户选择的步骤，读取预定义的代码。
    前端返回参数
    {
        target:[],
        features:[],

    }
    """

    def __init__(self, trainid, specificid, dataset_name, target, features, model_type, model_name, result_path, evaluate_methods=None):
        '''
        参数与前端的用户输入一致
        '''
        self.code_files = './codes/'
        self.trainid = str(trainid)
        self.specificid = str(specificid)
        self.dataset_name = dataset_name
        self.target = target
        self.features = features.split(';')
        self.model_type = str(model_type)
        self.model_name = str(model_name)
        self.result_path = result_path
        self.generate = ''
        self.evaluate_methods = evaluate_methods
        self.gen = ''


    def clean_data(self, df, cols, op, standard=''):
        '''
           自动数据清洗
           df:
           cols:
           op:数据清洗的操作
           '''
        if op == 'fillna':
            df.loc[:, cols].fillna()
        elif op == 'dropna':
            df.loc[:, cols].dropna()
        else:
            df.loc[:, cols].apply(op)
        return df

    def joint_code(self, code_path, encoding='utf-8'):
        '''拼接代码文件'''
        try:
            f = open(os.path.join(self.code_files, code_path), 'r', encoding=encoding)
            self.generate += f.read() + '\n'
        except:
            f = open(os.path.join(self.code_files, code_path), 'r', encoding='gbk')
            self.generate += f.read() + '\n'

    def get_code(self):
        '''生成代码'''
        # 拼接导入的库
        self.joint_code('ImportPackages.py')
        self.generate += '\n' + MODEL_DICT[self.model_type][self.model_name] + '\n'

        # 拼接函数评估方法
        if self.evaluate_methods:
            for method in self.evaluate_methods:
                self.joint_code(MODEL_DICT[method])

        # 拼接变量
        sklearn_model = MODEL_DICT[self.model_type][self.model_name].split(' ')[-1] + '()'

        self.generate += '''
FILE_PATH={}\n
FILE_PATH = np.unique(FILE_PATH)\n
FEATURES={}\n
TARGET='{}'\n
MODEL={}\n
model_name='{}'\n
TRAINID='{}'\n
DIR = '{}'\n
        '''.format(self.dataset_name, self.features, self.target, sklearn_model, self.model_name,  self.trainid, self.result_path)
        # 拼接主函数
        self.joint_code('Main.py')

        # 生成代码文件
        self.gen = 'generate.py'
        # self.gen = './Datasets/' + str(self.trainid) + '/' + self.model_name + '_generate.py'
        with open(self.gen, 'w', encoding='utf-8') as f:
            f.write(self.generate)
        f.close()



# if __name__ == '__main__':
#     trainid = 101
#     trainfiles = './Datasets/101/flex.csv;./Datasets/101/punch.csv'
#     type = 1
#     name = 103
#     a = SetModel(trainid, trainfiles, 'target', 'features', type, name)
#     a.get_code()
#
#     os.system('python generate.py gener')
#     # from generate import gener
#     # gener()






