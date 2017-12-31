#coding:utf-8
__author__ = 'equationl'

import requests
import time
import util
import json


class GetFullData(object):
    """
    获取说说的完整信息（包括完整评论，点赞的人等信息）
    """

    def __init__(self):
        self.session = requests.Session()
        self.headers = util.headers
        self.g_tk = util.g_tk
        self.tid = 0
        self.qq = 0

    def set_tid(self, tid):
        self.tid = tid

    def set_qq(self, qq):
        self.qq = qq

    def get_count_data(self):
        """
        获取统计数据信息
        :return:
        """
        url = util.parse_count_data_url(self.tid, self.qq)
        print(url)
        res = self.session.get(url, headers=self.headers)
        res_code = res.status_code
        if res_code != 200:
            print("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
            with open('crawler_log.log', 'a') as log_file:
                log_file.write("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
        content = res.text

        return content

    def get_like_list(self, is_first, begin_uin):
        """
        获取点赞数据
        :param is_first: 标记是否是第一页
        :param begin_uin: 如果不是第一页，则从哪条开始
        :return:
        """
        url = util.parse_likes_url(self.tid, self.qq)+"&if_first_page=%d&begin_uin=%d" % (is_first, begin_uin)
        print(url)
        res = self.session.get(url, headers=self.headers)
        res_code = res.status_code
        if res_code != 200:
            print("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
            with open('crawler_log.log', 'a') as log_file:
                log_file.write("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
        content = res.text

        return content

    def get_comments_list(self):
        """
        获取回复数据
        :return: 包含回复数据的一维数组（每20个数据一组）
        """
        content = []
        flag = True
        start = 0
        while flag:
            url = util.parse_comments_url(self.tid, self.qq)
            url = url+"&start="+str(start)
            print(url)
            res = self.session.get(url, headers=self.headers)
            res_code = res.status_code
            if res_code != 200:
                print("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
                with open('crawler_log.log', 'a') as log_file:
                    log_file.write("ERROR:Request Status Code is %d with %s \n" % (res_code, url))
            if '''"comments":''' in res.text:
                content.append(res.text)
            else:
                flag = False
            start += 20
        return content


class StartGetFullData(object):
    def __init__(self, qq, tid):
        """
        获取说说的更多数据
        :param qq:说说所属的qq号
        :param tid:说说id
        :return:
        """
        self.get_full_data_obj = GetFullData()
        self.get_full_data_obj.set_qq(qq)
        self.get_full_data_obj.set_tid(tid)
        self.qq = qq
        self.tid = tid

    def get_count(self):
        """
        获取说说的相关统计数据
        :return:
        """
        count = {"retweet": 0, "like": 0, "visit": 0}
        json_data = self.get_full_data_obj.get_count_data()
        json_data = json.loads(json_data[10:-2])
        #获取数据出错（反爬？）
        if json_data["code"] != 0:
            return count
        count_data = json_data["data"]
        if len(count_data) == 0:
            with open('crawler_log.log', 'a') as log_file:
                log_file.write('ERROR:Get count data in qq=%s tid=%s, %s\n' % (str(self.qq),
                                                                               str(self.tid),
                                                                               time.ctime()))

            return count
        count_data = count_data[0]["current"]
        count["retweet"] = count_data["cntdata"]["retweet"]
        count_data = count_data["newdata"]
        #获取统计数据出错（无返回数据）
        if len(count_data) <= 0:
            return count
        count["like"] = count_data["LIKE"]
        count["visit"] = count_data["PRD"]

        return count

    def get_likes(self):
        """
        获取点赞用户（经过测试，该接口并不能获取到全部点赞的人，目前暂未发现能拿到全部点赞的人的api）
        :return:
        """
        like = []
        like_data = self.__get_like_data(1, 0)
        for data in like_data:
            user = {"uid": data["fuin"], "addr": data["addr"].encode('latin1').decode('utf-8'),
                    "constellation": data["constellation"].encode('latin1').decode('utf-8'),
                    "gender": data["gender"].encode('latin1').decode('utf-8'),
                    "nick": data["nick"].encode('latin1').decode('utf-8')}
            like.append(user)

        like_data = self.__get_like_data(0, like[len(like)-1]["uid"])
        while len(like_data) > 0:
            for data in like_data:
                user = {"uid": data["fuin"], "addr": data["addr"].encode('latin1').decode('utf-8'),
                        "constellation": data["constellation"].encode('latin1').decode('utf-8'),
                        "gender": data["gender"].encode('latin1').decode('utf-8'),
                        "nick": data["nick"].encode('latin1').decode('utf-8')}
                like.append(user)
            like_data = self.__get_like_data(0, like[len(like)-1]["uid"])

        return like

    def get_comment(self):
        """
        获取回复数据
        :return:
        """
        comments = []
        json_datas = self.get_full_data_obj.get_comments_list()
        for json_data in json_datas:
            json_data = json.loads(json_data[10:-2])
            comments_data = []
            #在某些情况下的获取回复方式与一般不一样（如转发的说说），因为我不需要处理转发的说说，所以暂时做忽略处理
            try:
                comments_data = json_data["data"]["comments"]
            except KeyError:
                pass
            for data in comments_data:
                user = data["poster"]
                temp = {"content": data["content"], "time": data["postTime"], "qq": user["id"],
                        "nick": user["name"], "father": "", "cid": data["id"]}
                comments.append(temp)
                try:
                    replies = data["replies"]
                    for reply in replies:
                        user = reply["poster"]
                        temp = {"content": reply["content"], "time": reply["postTime"], "qq": user["id"],
                                "nick": user["name"], "father": data["id"], "cid": reply["id"]}
                        comments.append(temp)
                except KeyError:
                    pass

        return comments

    def __get_like_data(self, is_first, begin_uid):
        json_data = self.get_full_data_obj.get_like_list(is_first, begin_uid)
        json_data = json_data[10:-2]
        #不知道为什么会多出一个括号来
        if json_data[len(json_data)-1:] == ')':
            json_data = json_data[:-1]
        json_data = json.loads(json_data)
        like_data = json_data["data"]["like_uin_info"]

        return like_data