#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
获取动态详情

包含3个方法：
  make_dict -- 用于临时保存每个QQ的动态信息，QQ号为键，值为这个QQ号的所有动态的文件列表
  exact_mood_data -- 主要的功能函数，把动态信息从文件里提取出来，并调用insert_to_db方法插入到sqlite数据库中
  insert_to_db -- 供exact_mood_data调用，把数据插入到sqlite数据库中
"""

import os
import json
import sqlite3
import html
import get_full_data


class Get_detail(object):
    ''' Get moods detail information and save it to database'''

    def __init__(self, conn, cur):
        self.count = 0
        self.conn = conn
        self.cur = cur

    def make_dict(self):
        mood_dict = dict()
        dir_list = os.listdir('mood_result')
        for d in dir_list:
            file_list = os.listdir('mood_result/' + d)
            if len(file_list) != 1:
                mood_dict[d] = file_list
        return mood_dict

    def exact_mood_data(self, qq, content):
        '''Get mood data from files in result folder
        '''

        qqnumber = qq
        filename = fname
        '''with open(filename, encoding="utf-8") as f:
            con = f.read()'''  
        con_dict = json.loads(content[10:-2])
        try:
            moods = con_dict['msglist']
        except KeyError:
            return
        if moods == None:
            return

        mood_item = dict()
        mood_item['belong'] = qqnumber

        for mood in moods:
            mood_item['content'] = mood['content']
            mood_item['create_time'] = mood['created_time']
            mood_item['comment_num'] = mood['cmtnum']
            mood_item['phone'] = mood['source_name']
            mood_item['tid'] = mood['tid']
            mood_item['pic'] = mood['pic'][0]['url2'] if 'pic' in mood else ''
            mood_item['locate'] = mood['story_info']['lbs']['name'] if 'story_info' in mood else ''

            if mood_item['content'] == '' and mood_item['pic'] != '':
                # if the mood only has pic but no other thing
                mood_item['content'] = mood_item['pic']
            if mood_item['content'] == '' and 'rt_con' in mood:
                # 如果动态内容是一个转发的视频
                # 它会被保存在mood['rt_con']中
                try:
                    mood_item['content'] = mood['rt_con']['conlist'][0]['con']
                except IndexError:
                    mood_item['content'] = mood['rt_con']['conlist'][1]['con']
                except KeyError:
                    # when the mood only has a link
                    mood_item['content'] = mood['rt_con']['content']
                except TypeError:
                    # when the mood only has a video
                    mood_item['content'] = mood['video'][0]['url3']

            app = get_full_data.StartGetFullData(qq,  mood_item['tid'])

            print('Get count data with %d' % self.count)
            count_data = app.get_count()

            if count_data["like"] > 0:
                try:
                    print('Get like data with %d' % self.count)
                    like_data = app.get_likes()
                    self.insert_like_to_db(like_data, mood)
                except Exception as e:
                    print("ERROR in get like with count=%d info:%s\n" % (self.count, e))
                    with open('crawler_log.log', 'a') as log_file:
                        log_file.write("ERROR in get like with count=%d info:%s\n" % (self.count, e))

            if mood['cmtnum'] > 0:
                try:
                    print('Get comment data with %d' % self.count)
                    comment_data = app.get_comment()
                    self.insert_comment_to_db(comment_data, mood)
                except Exception as e:
                    print("ERROR in get comment with count=%d info:%s\n" % (self.count, e))
                    with open('crawler_log.log', 'a') as log_file:
                        log_file.write("ERROR in get comment with count=%d info:%s\n" % (self.count, e))

            mood_item["like"] = count_data["like"]
            mood_item["visit"] = count_data["visit"]
            mood_item["retweet"] = count_data["retweet"]

            print('Dealing with %d' % self.count)
            self.insert_mood_to_db(mood_item)

            self.count += 1
            self.conn.commit()
            if self.count % 1000 == 0:
                self.conn.commit()

    def insert_mood_to_db(self, mood):
        sql = 'INSERT INTO moods (qq, ctime,  content, comment_count, phone, image, locate, tid, like,' \
              ' visit, retweet)' \
              ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.cur.execute(sql, (mood['belong'], mood['create_time'], mood['content'], mood['comment_num'], mood['phone'],
                               mood['pic'], mood['locate'], mood['tid'], mood['like'], mood['visit'], mood['retweet']))

    def insert_like_to_db(self, like, mood):
        tid = mood["tid"]
        for row in like:
            sql = 'INSERT INTO likes (qq, tid, address, constellation, gender, nick)' \
                  ' VALUES (?, ?, ?, ?, ?, ?)'
            self.cur.execute(sql, (row["uid"], tid, row["addr"], row["constellation"], row["gender"], row["nick"]))


    def insert_comment_to_db(self, comment, mood):
        print(str(comment))
        tid = mood["tid"]
        for row in comment:
            sql = 'INSERT INTO comments (qq, tid, content, ctime, nick, father, cid) VALUES (?, ?, ?, ?, ?, ?, ?)'
            self.cur.execute(sql, (row["qq"], tid, row["content"], row["time"], row["nick"], row["father"], row["cid"]))


def start_write(qq, content):
    conn = sqlite3.connect('moods.db')
    cur = conn.cursor()

    app = Get_detail(conn, cur)

    app.exact_mood_data(qq, content)

    conn.commit()
    cur.close()
    conn.close()
