#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
本文件用于创建和删除sqlite数据表
方便保存QQ动态数据

使用方法：
在shell下
创建表： python3 operate_table.py create_table
删除表： python3 operate_table.py drop_table
'''
import sqlite3
import sys


class Operate_table(object):

    def __init__(self):
        self.conn = sqlite3.connect('moods.db')
        self.cur = self.conn.cursor()

    def create_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS moods (
                 id integer primary key Autoincrement not null,
                 qq int not null,
                 content text null,
                 comment_count int not null,
                 ctime int not null,
                 phone text null,
                 image text null,
                 locate text null,
                 tid text not null,
                 like int not null,
                 visit int not null,
                 retweet int not null)'''
        self.cur.execute(sql)

        sql = '''CREATE TABLE IF NOT EXISTS likes (
                 id integer primary key Autoincrement not null,
                 qq int not null,
                 tid text not null,
                 address text null,
                 constellation text null,
                 gender text null,
                 nick text not null)'''
        self.cur.execute(sql)

        sql = '''CREATE TABLE IF NOT EXISTS comments (
                 id integer primary key Autoincrement not null,
                 qq int not null,
                 tid text not null,
                 content text not null,
                 ctime int not null,
                 nick text not null,
                 father int null,
                 cid int not null)'''
        self.cur.execute(sql)

    def drop_table(self):
        self.cur.execute('drop table moods')

if __name__ == '__main__':
    app = Operate_table()
    argv = sys.argv[1]
    
    if argv == 'create_table':
        app.create_table()
    elif argv == 'drop_table':
        app.drop_table()
    else:
        print("输入参数必须为create_table或drop_table其中之一")
        raise ValueError
