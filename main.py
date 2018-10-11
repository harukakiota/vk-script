import vk
import time
from datetime import datetime as dt, time as t
from random import shuffle, uniform
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
                    time.sleep(1)
                    vk_apis.append(vk.API(session, v='5.71'))
                    time.sleep(1)
            date = 1523545215
            i = 0
            mint = 8
            maxt = 23
            likes = []
            while not stop_event.is_set():
                if mint <= dt.now().time().hour < maxt:
                    print(dt.now())
                    i += 1
                    result = vk_apis[0].wall.get(domain=config['domain'], count=1, filter='owner', v='5.71')
                    if result['items'][0]['date'] > date:
                        id = result['items'][0]['id']
                        owner = result['items'][0]['owner_id']
                        shuffle(vk_apis)
                        for el in vk_apis:
                            likes.append(el.likes.add(type='post', item_id=id, owner_id=owner, v='5.71'))
                            time.sleep(uniform(15,25))
                        toc = time.time()
                        date = result['items'][0]['date']
                        print('likes were put in ' + str(toc - date) + ' seconds')
                        for i in range(len(vk_apis)):
                            print(str(likes[i]) + ' ' + str(vk_apis[i].account.getProfileInfo()['last_name']))
                            time.sleep(0.34)
                        print(dt.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
                        winsound.PlaySound('clonk.wav', winsound.SND_FILENAME)
                        print('New post')
                        likes = []
                        # time.sleep(800)
                    elif (dt.now().time().minute == 0) & (dt.now().time().second < 20) | (dt.now().time().minute == 59) & (dt.now().time().second > 45):
                        print(i)
                        time.sleep(0.34)
                    else:
                        print(i)
                        time.sleep(10)
                else:
                    print("I'm going to start working in " + str((mint - dt.now().time().hour)) + " hours")
                    time.sleep(500)
        except:
            print("I want to work, but I can't")
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)

global pill2kill, t, checkedArr, flag, config

config = load_config()

root = tk.Tk()
root.title("Likes")

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
