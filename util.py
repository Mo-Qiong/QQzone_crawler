#coding:utf-8

from urllib import parse
import os

def get_cookie():
    '''Get cookie from cookie_file'''
    with open('cookie_file') as f:
        cookie = f.read()
    cookie = cookie.replace('\n', '')

    return cookie

cookie = get_cookie()

headers = {'host': 'h5.qzone.qq.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': cookie,
            'connection': 'keep-alive'}

def get_g_tk():
    ''' make g_tk value'''

    pskey_start = cookie.find('p_skey=')
    pskey_end = cookie.find(';', pskey_start)
    p_skey = cookie[pskey_start+7: pskey_end]

    h = 5381

    for s in p_skey:
        h += (h << 5) + ord(s)

    return h & 2147483647

g_tk = get_g_tk()

def parse_moods_url(qqnum):
    '''This method use to get every friend's mood cgi url
       So it needs the friend's qqnumber to get their url
    '''

    params = {"cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
              "code_version": 1,
              "format": "jsonp",
              "g_tk": g_tk,
              "hostUin": qqnum,
              "inCharset": "utf-8",
              "need_private_comment": 1,
              "notice": 0,
              "num": 20,
              "outCharset": "utf-8",
              "sort": 0,
              "uin": qqnum}
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?"

    url = host + parse.urlencode(params)
    return url

def parse_friends_url():
    '''This method only generate the friends of the owner
       So do not need to get qq number, just get it from
       self cookie
    '''

    cookie = headers['Cookie']
    qq_start = cookie.find('uin=o')
    qq_end = cookie.find(';', qq_start)
    qqnumber = cookie[qq_start+5 : qq_end]
    if qqnumber[0] == 0:
        qqnumber = qqnumber[1:]
    params = {"uin": qqnumber,
              "fupdate": 1,
              "action": 1,
              "g_tk": g_tk}

    host = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?"
    #https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?uin=284182470&fupdate=1&action=1&offset=200&g_tk=1350570173&qzonetoken=8114052f3d145601114b9b3f8caad4ad2853b418b9c345f42af296d6d3e2c980b592a1b7c52273aaa0
    url = host + parse.urlencode(params)

    return url


def parse_likes_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param begin_uid: 获取起点（qq）
    :return:
    """
    #cookie中储存的qq号似乎前面加了一个英文字母 o ？
    user_qq_num = cookie[cookie.find("uin=")+5:]
    user_qq_num = user_qq_num[:user_qq_num.find(";")]
    user_qq_num = int(user_qq_num)
    unikey =  '''http://user.qzone.qq.com/'''+qq+'''/mood/'''+mood_id
    params = {"g_tk": g_tk,
              "unikey": unikey,
              "query_count": 60,
              "uin": user_qq_num}
    host = "https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?"

    url = host + parse.urlencode(params)
    return url


def parse_count_data_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param qq: 所属qq
    :return:
    """
    unikey = '''http://user.qzone.qq.com/'''+qq+'''/mood/'''+mood_id
    params = {"unikey": unikey,
              "fupdate":1,
              "g_tk": g_tk}
    host = "https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/user/qz_opcnt2?"

    url = host + parse.urlencode(params)
    return url


def parse_comments_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param qq: 所属qq
    :return:
    """
    topic_id = qq+"_"+mood_id
    params = {"need_private_comment": 1,
              "hostUin": qq,
              "num": 20,
              "order": 0,
              "topicId": topic_id,
              "format": "jsonp",
              "g_tk": g_tk
              }
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_getcmtreply_v6?"

    url = host + parse.urlencode(params)
    return url


def parse_mood_data_url(qq_num, mood_id, count):
    """
    :param qq_num: 所属id
    :param mood_id: 说说id
    :param count: 查询数量
    :return:
    """
    unikey = "http%3A%2F%2Fuser.qzone.qq.com%2F754237716%2Fmood%2F"+mood_id
    params = {"g_tk": g_tk,
              "unikey": unikey,
              "begin_uid": 0,
              "query_count": count,
              "if_first_page": 1,
              "uin": qq_num}
    host = "https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?"

    url = host + parse.urlencode(params)
    return url


def check_path(path):
    '''This method use to check if the path is exists.
       If not, create that
    '''

    if not os.path.exists(path):
        os.mkdir(path)
