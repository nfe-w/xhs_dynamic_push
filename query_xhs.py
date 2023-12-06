# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time: 2023/12/06 21:07

import json
from collections import deque

from bs4 import BeautifulSoup

import util
from logger import logger
from push import push

DYNAMIC_DICT = {}
LEN_OF_DEQUE = 50


def query_dynamic(uid=None):
    if uid is None:
        return
    query_url = f'https://www.xiaohongshu.com/user/profile/{uid}'
    headers = get_headers()
    response = util.requests_get(query_url, '查询动态状态', headers=headers, use_proxy=True)
    if util.check_response_is_ok(response):
        html_text = response.text
        soup = BeautifulSoup(html_text, "html.parser")
        scripts = soup.findAll('script')
        result = None
        for script in scripts:
            if script.string is not None and 'window.__INITIAL_STATE__=' in script.string:
                try:
                    result = json.loads(script.string.replace('window.__INITIAL_STATE__=', '').replace('undefined', 'null'))
                except TypeError:
                    logger.error(f'【查询动态状态】json解析错误，uid：{uid}')
                    return None
                break

        if result is None:
            logger.error(f'【查询动态状态】请求返回数据为空，uid：{uid}')
        else:
            user_name = result['user']['userPageData']['basicInfo']['nickname']
            notes = result['user']['notes'][0]
            if len(notes) == 0:
                logger.info(f'【查询动态状态】【{user_name}】动态列表为空')
                return

            note = notes[0]
            note_id = note['id']

            if DYNAMIC_DICT.get(uid, None) is None:
                DYNAMIC_DICT[uid] = deque(maxlen=LEN_OF_DEQUE)
                for index in range(LEN_OF_DEQUE):
                    if index < len(notes):
                        DYNAMIC_DICT[uid].appendleft(notes[index]['id'])
                logger.info(f'【查询动态状态】【{user_name}】动态初始化：{DYNAMIC_DICT[uid]}')
                return

            if note_id not in DYNAMIC_DICT[uid]:
                previous_note_id = DYNAMIC_DICT[uid].pop()
                DYNAMIC_DICT[uid].append(previous_note_id)
                logger.info(f'【查询动态状态】【{user_name}】上一条动态id[{previous_note_id}]，本条动态id[{note_id}]')
                DYNAMIC_DICT[uid].append(note_id)
                logger.info(DYNAMIC_DICT[uid])

                dynamic_time = ''

                note_card = note['noteCard']
                content = note_card['displayTitle']
                pic_url = note_card['cover']['infoList'][0]['url']
                jump_url = f"https://www.xiaohongshu.com/explore/{note_card['noteId']}"
                logger.info(f'【查询动态状态】【{user_name}】动态有更新，准备推送：{content[:30]}')
                push.push_for_xhs_dynamic(user_name, note_id, content, pic_url, jump_url, dynamic_time)


def get_headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
