import vk
import re
import time
from datetime import datetime as dt, time as t
from random import shuffle, uniform, randint
import winsound
import tkinter as tk
import threading
from helper import load_config

def go():
    global flag, t, pill2kill, checkedArr
    if not flag:
        print('Entered the threading')     
        t.start()
        flag = True
        print('Started')
    else:
        print('Already started')
        pill2kill = threading.Event()
        t = threading.Thread(target=work, args=(checkedArr, pill2kill))
        t.start()

def stop():
    print('Trying to stop')
    pill2kill.set()
    t.join()
    print('Stopped')

def refresh(vk_api, owner_id, post_id):
    get_offset = vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, sort='asc', count = 1, extended=1, v='5.71')
    if get_offset['count'] > 100:
        offset = int(get_offset['count'])
    else:
        offset = 100
    result_comments = vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, sort='asc', offset=offset-100, count = 100, v='5.71')
    comments = result_comments['items']

    stop_str = 'СТОП!'
    begin_str = 'новый раунд'
    
    letters = ['А', 'Б', 'В', 'Г', 'Д']
    used_answers = []
    begin_date = 0
    end_date = -1
    pattern1 = re.compile(r'[А-Да-д]\d{1,2}')
    pattern2 = re.compile(r'\d{1,2}[А-Да-д]')
    for comment in comments:
        if comment['text'].find('На сегодня рыбалка окончена.') != -1:
            return None
        if comment['text'].find(begin_str) != -1:
            begin_date = comment['date']
        if comment['text'].find(stop_str) != -1:
            end_date = comment['date']

    for comment in comments:
        if (pattern1.match(comment['text']) != None) & (comment['date'] > begin_date):
            number = comment['text'][1:len(comment['text'])]
            letter = comment['text'][0:1].capitalize()
            used_answers.append(letter + number)

        elif (pattern2.match(comment['text']) != None) & (comment['date'] > begin_date):
            letter = comment['text'][len(comment['text'])-1:len(comment['text'])].capitalize()
            number = comment['text'][0:len(comment['text'])-1]
            used_answers.append(letter + number)

    answer_bank = []
    for i in range(1,16):   
        for letter in letters:
            check_str = letter+str(i)
            if not check_str in used_answers:
                answer_bank.append(check_str)
    return [answer_bank, begin_date, end_date]

def check_current_game(vk_apis, ended_game_date): # идёт ли в данный момент вообще игра 
    global config
    get_post = vk_apis[0].wall.get(domain=config['domain'], count=20, filter='owner', v='5.71')
    for item in get_post['items']: 
        if item['text'].find('ловлютунца') != -1:
            if item['date'] == ended_game_date: # совпадает ли игра с закешированной
                print('Нового поста не появилось')
                return None
            else:
                print('Найден новый пост от ' + dt.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S'))
                return item

def delete_reposts(vk_apis):
    #TODO 
    return

def make_reposts(vk_apis):
    #TODO
    return
        
def work(checkedArr, stop_event):
    global config
    while not stop_event.is_set():
        try:
            app_id = config['app_id']
            users = config['users']
            vk_apis = []
            for i in range(len(config['users'])):
                if checkedArr[i].get():
                    session = vk.AuthSession(app_id, users[i]['login'], users[i]['password'], scope='wall,account')
                    vk_apis.append(vk.API(session, v='5.71'))
                    print(str(vk_apis[-1].account.getProfileInfo()['last_name']))
                    time.sleep(uniform(180, 480))
            
            old_begin_date = -1
            ended_game_date = -1
            current_game = check_current_game(vk_apis, ended_game_date)
            while not stop_event.is_set():
                if (current_game != None) & (8 <= dt.now().time().hour < 23):
                    refresh_result = refresh(vk_apis[0], current_game['owner_id'], current_game['id'])
                    while refresh_result != None:
                        answer_bank, begin_date, end_date = refresh(vk_apis[0], current_game['owner_id'], current_game['id'])
                        if old_begin_date != begin_date:
                            print('Новый раунд начался')
                            flag_new_round = True
                        else:
                            flag_new_round = False
                        if (end_date < begin_date) & (flag_new_round == True):
                            shuffle(vk_apis)
                            for el in vk_apis:
                                refresh_result = refresh(vk_apis[0], current_game['owner_id'], current_game['id'])
                                if refresh_result != None:
                                    answer_bank = refresh_result[0]
                                    for i in range(2):
                                        if not stop_event.is_set():
                                            index = randint(0, len(answer_bank))
                                            rand_message = answer_bank[index]
                                            print('Выбран ответ ' + rand_message)
                                            answer_bank.pop(index)
                                            el.wall.createComment(owner_id=current_game['owner_id'], post_id=current_game['id'], message=rand_message, v='5.71')
                                            print('Осталось ' + str(len(answer_bank)) + ' вариантов')
                                            time.sleep(uniform(5,15))
                                        else:
                                            print('Stopping')
                                            break
                                else:
                                    print('Во время записи ответов администрация прекратила игру')
                                    break
                                print('Ответы записаны для одного участника')
                                sleep = uniform(200, 450)
                                print('Следующий будет спать ' + str(sleep) + ' секунд')
                                time.sleep(sleep)
                            flag_new_round = False
                        else:
                            print(dt.now())
                            print('Новый раунд ещё не начался')
                            time.sleep(300)
                        old_begin_date = begin_date

                    ended_game_date = current_game['date']
                    print('Администраторы написали, что игра окончена на сегодня')
                    delete_reposts(vk_apis)
                else:
                    print(dt.now())
                    print('На сегодня окончена и ещё не началась')
                    time.sleep(1000)
                current_game = check_current_game(vk_apis, ended_game_date)
        except:
            print("I want to work, but I can't")
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
            time.sleep(500)

global pill2kill, t, checkedArr, flag, config

config = load_config()

root = tk.Tk()
root.title("Battleship")

checkedArr = []
for i in range(len(config['users'])):
    checkedArr.append(tk.IntVar())
    button = tk.Checkbutton(root, text = config['users'][i]['name'] + ' ' + config['users'][i]['surname'], variable = checkedArr[-1]).grid(sticky='W')

flag = False
pill2kill = threading.Event()
t = threading.Thread(target=work, args=(checkedArr, pill2kill))
button = tk.Button(root, text="Go", command=go).grid(row = 7, column = 0, sticky = 'E')
slogan = tk.Button(root, text="Stop", command=stop).grid(row = 7, column = 1, sticky = 'W')

root.mainloop()
