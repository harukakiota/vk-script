import vk
import re
import time
from datetime import datetime as dt, time as t
from random import shuffle, uniform
import winsound
from helper import load_config


def work():
    config = load_config()
    app_id = config['app_id']
    login = config['users'][0]['login']
    password = config['users'][0]['password']
    session = vk.AuthSession(app_id, login, password, scope='wall,account')
    time.sleep(1)
    vk_api = vk.API(session0, v='5.71')
    time.sleep(1)
    
    post_id = config['post_id']

    result = vk_api0.wall.get(domain=config['domain'], offset=1, count=1, filter='owner', v='5.71')
    owner = result['items'][0]['owner_id']
    count = 0
    i = 0
    while True:
        new_comments = vk_api0.wall.getComments(owner_id = owner, post_id = post_id, start_comment_id = 29975)
        print(dt.now())
        if new_comments['count'] > count:
            i += 1
            comment = vk_api0.wall.createComment(owner_id = owner, post_id = post_id, message = '11', v='5.71')
            sleep = uniform(10, 20)
            print('Sleepy time = ' + str(sleep))
            time.sleep(sleep)
            print('New comment ' + str(i))
            count = new_comments['count'] + 1
        else:
            count = new_comments['count']
        time.sleep(5)



while True:
    try:
        work()
    except:
        print("I want to work, but I can't")
        winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)