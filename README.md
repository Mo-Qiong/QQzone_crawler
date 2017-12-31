## 关于
Edit by equationl

该项目修改自 xjr7670 的 [QQzone_crawler](https://github.com/xjr7670/QQzone_crawler)
原作者说明： [QQ空间动态爬虫](https://zhuanlan.zhihu.com/p/24656161)

#### 修改了什么？
* 爬取完整的评论列表
* 爬取点赞的人
* 爬取说说的浏览量等更多信息
* 简化运行操作，默认不保存元数据，直接整理后存进数据库（有需要更多数据或元数据的请自行修改）

## 快速开始
将 cookie 存入 cookie_file 参照一下两种方式运行
#### 方法1 遍历爬取所有好友的说说
``
python main.py
``

#### 方法2 爬取指定一个好友的说说
``
python main.py qq_number
``
如：
``
python main.py 123456
``
## 数据库结构
默认将数据储存于 ./moods.db
#### 表 moods 说说相关数据
* id integer primary key Autoincrement not null
* qq int not null   说说所属qq
* content text null 说说内容
* comment_count int not null    说说的回复数量
* ctime int not null    说说的发表时间
* phone text null   发表说说时的手机标志
* image text null   说说配图地址
* locate text null  说说定位信息
* tid text not null 说说id
* like int not null 说说的点赞数
* visit int not null    说说的浏览量
* retweet int not null  说说的转发量

#### 表 likes 点赞用户数据
* id integer primary key Autoincrement not null
* qq int not null   点赞者qq
* tid text not null 点赞所属说说id
* address text null 点赞者地址
* constellation text null   点赞者星座
* gender text null  点赞者性别
* nick text not null    点赞者昵称

#### 表 comments 回复相关数据
* id integer primary key Autoincrement not null
* qq int not null   回复者qq号
* tid text not null 回复所属说说
* content text not null 回复内容
* ctime int not null    回复时间
* nick text not null    回复者昵称
* father int null  二级回复的上级id
* cid int not null  回复id（不唯一）

## <font color="red">注意事项</font>
* 程序运行日志为 ./crawler_log.log
* 获取元数据或更多数据请修改 `./get_full_data.py` 文件中的 `StartGetFullData()` 类的 `get_count()`、`get_likes()`、`get_comment()` 方法
* 默认爬取延时为 20s ，原作者给的 5s 在其他接口都不会被反爬，但是获取点赞列表容易 403 。需要更改延时的请在 `./get_moods.py` 中修改

### 以下为原项目信息
***

## QQzone_crawler
QQ 空间动态爬虫，利用cookie登录获取所有可访问好友空间的动态并保存到本地

需要先安装第三方库 **requests**
本程序使用的是**python3.5**，在**Linux**下完成。由于自己的电脑上同时有python2.7和python3.5，默认是python2。所以在每个程序头部我写的都是

```
#/usr/bin/env python3
```

配置不一样的朋友需要自己稍做修改。

由于程序使用`from urllib import parse`，利用parse模块来构造URL，所以如果使用python2的朋友需要在对应的地方修改，此外print语句也是要相应修改的。

> 方程注：1.已测试 windows 能完美运行。2.程序头在原作者的更新中已经被去掉，使用 python2.x 运行只需注意 print 语句和 parse 的修改


# 各程序文件说明

**main.py**： 程序主入口，运行时执行`python3 main.py`即可

**get_my_friends.py**： 用于从QQ空间服务器获取包括自己的QQ好友信息的文件，其中包括他们的QQ号和名称（此处是备注名），保存到本地，每个文件中保存有50个。每完成一个文件请求后，会暂停5秒。在程序运行时，会自动将这些文件保存在friends文件夹中。

**get_qq_number.py**： 用于从上一步保存好的文件中提取出所有好友的QQ号和名称，QQ号和名称以字典形式保存，再以它们组成的字典为作元素构造列表，再保存到本地，文件名为qqnumber.inc

**get_moods.py**： 用于从QQ空间服务器获取包含每个好友空间发表的说说的文件，其中包含每个说说的发表时间、内容、地点信息、手机信息等，保存到本地，每个文件中保存20条信息。每完成一个文件请求后，会暂停5秒。在程序运行时，会自动将这些文件保存在mood_result文件夹中。

**cookie_file**： 用于放置自己登录QQ空间后得到的cookie。从浏览器中复制出来，默认是会分行的，不用管它，在负责处理cookie的函数中已有对应的处理代码。但由于我是在Linux下利用替换的方式替换掉换行符，所以如果在windows下运行，可能还需要在这里处理一下。**但要注意的是，这个文件里面只能放一个cookie。它的作用是方便设置cookie，而不是用于反反爬虫。**

---

**operate_table.py**：这个程序创建用于保存说说信息的数据库。里面写了创建数据表和删除数据表的两个函数。需要单独执行。
创建数据表：

```
python operate_table.py create_table
```

删除数据表：

```
python operate_table.py drop_table
```

> 方程注：数据库操作已写入 main.py 无需使用者自行运行

**get_moods_detail.py**：程序在执行完get_moods.py中的功能之后，会把包含有每个好友的说说文件保存到本地。而这个程序就是用于把说说信息从这些文件里面提取出来，放到sqlite数据库里面去的。这个程序需要单独执行。执行完后在当前目录下会生成moods.sqlite数据库文件。本程序需要在成功执行operate_table.py程序创建数据表后执行。

**get_single_report**：这个是个Web程序，用于在浏览器中查看指定好友说说的简单报告。也需要单独执行，并且必须要在执行完get_moods_details.py文件以生成moods.sqlite数据库文件，这个web程序才可以正确执行。直接执行本文件夹中的index.py即可。需要先安装flask、pandas、sqlalchemy这3个库。执行index.py后，在浏览器中输入 http://localhost/qqnum=QQ号码 就可以查看到结果了

> 方程注：1.已修改为请求完成后直接解析数据并储存至数据库，无需手动运行 get_moods_detail.py 2.已删除 get_single_report 相关文件，有需要的请自行前往原项目拷贝

## <font color="red">注意事项</font>

1. **获取QQ好友信息是间接获取的。需要先在QQ空间中将自己空间的访问权限先设置为仅QQ好友可访问。然后程序才能够正常运行**

2. 最终获取到的各好友的空间动态会以文件形式保存在以其QQ号为名的文件夹当中（它们又位于mood\_result文件夹中）。它们是由QQ空间服务器返回的文件，还需要自行进行处理才能得到自己想要的信息。其实内容的格式已经很接近JSON了
2.1 更新后的版本，可以通过依次执行operate_table.py、get_moods_detail.py两个程序来把动态保存在sqlite数据库文件中

3. 在get_moods_detail.py程序中，我只提取了当时所需要的部分信息，而不是与说说相关的所有信息。有需要其它信息的还要自己去operate_table.py中修改创建数据表的函数以及在get_moods_detail.py程序中修改提取说说信息的函数