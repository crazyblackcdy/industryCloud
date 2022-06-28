##quick_ml  

### __属性名称为大写！！__  

###modules 训练模型表
| 属性名 | 类型 | 作用意义 |  
| ---- | ---- | ---- |  
| MODULEID | Integer | 主键；标记不同模型 |  
| TYPE | Integer | 标记不同类型训练方式（回归、分类等） |
| TYPENAME | String(32) | 不同类型训练方式名称 | 
| NAME | String(64) | 模型名 | 
| IMPORTING | String(128) | 模型需要import的语句|

### accounts  账户（用户名）表
| 属性名 | 类型 | 作用意义 |  
| ---- | ---- | ---- | 
| USERNAME | String(32) | 主键；用户名 | 
| PASSWORD | String(32) | 用户密码 | 
| EMAIL | String(128) | 用户邮箱 | 

### trains  训练项目表
| 属性名 | 类型 | 作用意义 |  
| ---- | ---- | ---- | 
| TRAINID | Integer | 主键；训练项目id，标记不同的训练项目 | 
| USERNAME | String(32) | 外键accounts.username；提交此训练项目的用户，用于跨表检索 | 
| TRAINFILES | String(256) | 上传的训练项目的文件的所在地址，文件之间用英文分号（;）隔开 | 
| USEPCA | Boolean | 默认为True，表示该训练项目是否使用降维 |
| STARTTIME | DateTime | 提交训练项目的时间（此数据类型需要验证是否可行） | 
| TRAINFINISHED | Boolean | 默认为False，整个训练项目完成后改为True；标记该训练是否完成 | 

### results 具体训练结果表
| 属性名 | 类型 | 作用意义 |  
| ---- | ---- | ---- | 
| SPECIFICID | Integer | 主键；每次训练中的具体训练模型 | 
| TRAINID | Integer | 外键trains.trainID；此具体训练所属的训练（项目），用于跨表检索 | 
| MODULEID | Integer | 外键modules.moduleID；此具体训练的模型id，用于跨表检索 | 
| RUNNINGTIME | Float | 模型运行时间，输出需要加s | 
| ACCURACY | Float | 训练正确率，输出需要加% | 
| IMGPATH_CONFUSION | String(64) | 生成混淆矩阵图片所在位置 | 
| FINISHED | Boolean | 默认为False；标记该具体训练是否完成 | 

