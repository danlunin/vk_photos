import os
import vk
import urllib
from selenium import webdriver
import time
from tkinter import *
from tkinter.ttk import *

def authorize(app_id):
    driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
    driver.get(
        'http://oauth.vk.com/authorize?client_id=' + app_id + '&scope=' + 'messages' + '&redirect_uri=' + 'https://oauth.vk.com/blank.html' + '&display=' + 'page' + '&response_type=token')
    while (driver.current_url.find('access') == -1):
        time.sleep(3)
    #print(driver.current_url)
    url_str = driver.current_url
    first = url_str.find('=')
    last=url_str.find('&')
    access_token = url_str[first+1: last]
    #print(access_token)
    session = vk.Session(access_token)
    driver.close()
    return  vk.API(session)

def get_dialogs(vk_api, number_of_dialogs, offset):
    return vk_api.messages.getDialogs(count=number_of_dialogs, version=5.73, offset=offset)

def get_photos(vk_api, dialogs, number_of_messages, local_address, big_images):
    progress = get_progressbar()
    progress['maximum'] = len(dialogs)*number_of_messages
    iter = 0
    image_size = 'src_big' if big_images else 'src'
    for i in range(1, len(dialogs)):
        peer = dialogs[i]['uid']
        atach = vk_api.messages.getHistoryAttachments(peer_id=peer, media_type='photo', count=number_of_messages, version=5.73)
        for e in atach:
            if (str(e) =='0' or e== 'next_from'):
                continue
            iter+=1
            try:
                urllib.request.urlretrieve(atach[e]['photo'][image_size],
                                           os.getcwd() + local_address + "\\" + str(iter) + '.jpg')
                progress['value'] = iter
                progress.update()
            except Exception as err:
                #print('e: ' + str(atach[e]) + '  ' + str(e))
                print(err)
                continue
    progress.quit()

def get_progressbar():
    frame = Tk()
    frame.title('Downloading photos')
    pb = Progressbar(frame,
                     orient='horizontal', length=256,
                     mode='determinate')
    pb.grid(column=0, row=3, pady=2)
    pb['maximum'] = 100
    return pb

def start_app(number_of_dialogs, number_of_messages, big_images, local_photo_address, from_dialog, app_id):
    local_photo_address = '\\' + local_photo_address
    if (not os.path.exists(os.getcwd()  + local_photo_address)):
        os.makedirs(os.getcwd() + local_photo_address)
    vk_api = authorize(app_id)
    dialogs = get_dialogs(vk_api, number_of_dialogs, from_dialog)
    #print(dialogs)
    get_photos(vk_api, dialogs, number_of_messages, local_photo_address, big_images)

def form_gui_and_launch(title, local_photo_address, app_id):
    master = Tk()
    master.title(title)
    Label(master, text="Number of dialogs").grid(row=0)
    Label(master, text="Number of photos from each dialog").grid(row=1)
    Label(master, text="Name for local folder").grid(row=2)
    Label(master, text="Start from dialog number(optional)").grid(row=3)
    default_dialogs = IntVar(master, value=100)
    default_photos_in_dialog = IntVar(master, value=100)
    default_folder_name = StringVar(master, value=local_photo_address)
    default_start_messge = IntVar(master, value=0)
    e1 = Entry(master, textvariable=default_dialogs)
    e2 = Entry(master, textvariable=default_photos_in_dialog)
    e3 = Entry(master, textvariable=default_folder_name)
    e4 = Entry(master, textvariable=default_start_messge)
    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    e4.grid(row=3, column=1)
    var1 = IntVar()
    Checkbutton(master, text="Small images", variable=var1).grid(row=4, sticky=W)
    Button(master, text='Quit', command=master.quit).grid(row=5, column=0, sticky=W, pady=4)
    Button(master, text='Start session',
           command=lambda: start_app(int(e1.get()), int(e2.get()), var1.get() == 0, e3.get(), e4.get(), app_id)).grid(row=5,
                                                                                                              column=1,
                                                                                                              sticky=W,
                                                                                                              pady=4)
    mainloop()

def main():

    local_photo_address = "photos_from_vk"
    form_gui_and_launch("VK photo downloader", local_photo_address, app_id)



if __name__ == '__main__':
    main()
