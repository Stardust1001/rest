# rest

本框架基于 flask，是一个专注于 database to restful-api 的框架，您几乎无需编写额外后端代码，就可以为您的数据库创建一套增、删、改、查的接口

## 起步

### 1. 检查您的 database
这一步，您只需检查要进行增删改查操作的 database，查看其中的每一个 table，是否都有一个自动递增的整数型字段id，如果没有，请添加它

### 2. 修改config.py
这里，是配置您的数据库连接信息的地方

### 3. 运行程序，并按照约定的方式在前端调用框架封装好的接口
在 pip install 相关依赖包后，输入 python3 main.py 即可运行后端程序<br/>

#### 3.1 GET 请求
GET 请求允许您获取某个table指定id的数据<br/>
接口地址：/restful?model={model}&id={id}

#### 3.2 POST 请求
POST 请求支持添加数据和查询数据两个功能<br/>
查询数据<br/>
接口地址：/restful?model={model}&command=add<br/>
POST请求体：JSON数据
查询数据<br/>
接口地址：/restful?model={model}&command=search<br/>
POST请求体：JSON参数

#### 3.3 PUT 请求
PUT 请求允许您更新某个table的指定id的数据<br/>
接口地址：/restful?model={model}&id={id}<br/>
PUT请求体：JSON数据

#### 3.4 DELETE 请求
DELETE 请求支持您删除某个table的指定id的数据<br/>
接口地址：/restful?model={model}&id={id}

### 4. 查询接口的其他参数和功能
page 属性用于分页<br/>
limit 属性是每一页的条数<br/>
attributes 属性允许您仅获取需要的字段<br/>
order 属性允许你设置多个排序<br/>
op 属性里是多条件查询功能<br/>
op.where 是普通的 where 条件<br/>
此外，还有 op.lte, op.gte, op.lt, op.gt, op.like, op.or 等等，对应SQL里相关操作<br/>

## 示例
示例1<br/>
![1.png](https://i.loli.net/2021/06/10/Pvz37ioDNkatIOT.png)<br/><br/>
示例2<br/>
![2.png](https://i.loli.net/2021/06/10/389NHEUkIJdhaqt.png)<br/><br/>
示例3<br/>
![3.png](https://i.loli.net/2021/06/10/3PZa94iEYxjG1lk.png)<br/><br/>
示例4<br/>
![4.png](https://i.loli.net/2021/06/10/kqZ1w5brXaDcNWQ.png)<br/><br/>
示例5<br/>
![5.png](https://i.loli.net/2021/06/10/kMWLhmDvb3jt1Ir.png)<br/><br/>
示例6<br/>
![6.png](https://i.loli.net/2021/06/10/rifcRht43H6vj8s.png)<br/><br/>
示例7<br/>
![7.png](https://i.loli.net/2021/06/10/ayzXwpDW89nl7Kj.png)<br/><br/>

