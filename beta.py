# -*- coding:utf-8 -*-
from tkinter import END
from tkinter import EXTENDED
from tkinter import ttk
from urllib import parse
import json
import os
import requests
import threading
import tkinter as tk

columns1 = ("TITLE", "ID")
headers = {
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/72.0.3626.96 Safari/537.36')}


def open_link():
    listbox_audio_name.delete(0, END)
    listbox_audio_url.delete(0, END)
    name = parse.quote(entry_search_text.get())
    link = entry_url.get()
    albumId = link.split('/')[4]
    url = 'http://180.153.255.6/mobile/v1/album/track/ts-1534855383505?albumId=' + albumId + \
        '&device=android&isAsc=true&isQueryInvitationBrand=true&pageId=1&pageSize=20&pre_page=0'
    html = requests.get(url)
    all = json.loads(html.text)
    # Thread2 = futures.ThreadPoolExecutor(max_workers=1)
    total_pages = all['data']['totalCount']
    pages_list = range(1, total_pages + 1)
    for n in pages_list:
        url = 'https://www.ximalaya.com/revision/search?core=album&kw=' + name + \
            '&page=' + str(n) + '&spellchecker=true&rows=20&condition=relation&device=iPhone'
        # print(url)
        html = requests.get(url, headers=headers)
        all = json.loads(html.text)
        data = all['data']['result']['response']['docs']
        # print(data)
        for x in data:
            title = x['title']
            id = x['id']
            treeview_album.insert('', 'end', values=(title, id))
    show_status('解析专辑成功\n')


def download():
    path = entry_download_dir.get()
    if not os.path.isdir(path):
        os.makedirs(path)

    xuanzhong_index = listbox_audio_name.curselection()
    show_status('' + str(len(xuanzhong_index)) + '个任务正在下载\n')
    for n in range(0, len(xuanzhong_index)):
        name = listbox_audio_name.get(xuanzhong_index[n])
        url = listbox_audio_url.get(xuanzhong_index[n])
        file_name = path + '/' + name + '.mp3'
        file1 = requests.get(url, headers=headers)
        with open(file_name, 'wb') as code:
            code.write(file1.content)
        show_status('[' + file_name + '] 下载成功\n')


def solve():
    show_status('解析线程开始\n')
    listbox_audio_name.delete(0, END)
    listbox_audio_url.delete(0, END)
    for item in treeview_album.selection():
        item_text = treeview_album.item(item, 'values')
        albumId = item_text[1]
    url = 'http://180.153.255.6/mobile/v1/album/track/ts-1534855383505?albumId=' + albumId + \
        '&device=android&isAsc=true&isQueryInvitationBrand=true&pageId=1&pageSize=20&pre_page=0'
    html = requests.get(url)
    all = json.loads(html.text)
    # total_counts = all['data']['totalCount']
    maxPageId = all['data']['maxPageId']
    # last_page_totals = int(total_counts)%20
    list1 = range(1, maxPageId + 1)
    for n in list1:
        url = 'http://180.153.255.6/mobile/v1/album/track/ts-1534855383505?albumId=' + albumId + \
            '&device=iPhone&isAsc=true&isQueryInvitationBrand=true&pageId=' + \
              str(n) + '&pageSize=20&pre_page=0'
        html = requests.get(url)
        all = json.loads(html.text)
        data = all['data']['list']
        for a in data:
            # print(a)
            title = a['title']
            playUrl64 = a['playUrl64']
            listbox_audio_name.insert(END, title)
            listbox_audio_url.insert(END, playUrl64)
    show_status('解析线程结束\n')


def clear_list(tree):
    x = tree.get_children()
    for item in x:
        tree.delete(item)


def search():  # 按照关键词进行搜索
    show_status('搜索线程开始\n')
    clear_list(treeview_album)
    name = parse.quote(entry_search_text.get())
    url = 'https://www.ximalaya.com/revision/search?core=album&kw=' + \
        name + '&spellchecker=true&rows=20&condition=relation&device=iPhone'
    html = requests.get(url, headers=headers)
    all = json.loads(html.text)
    # data = all['data']['result']['response']['docs']
    # print(data)
    total_pages = all['data']['result']['response']['totalPage']
    pages_list = range(1, total_pages + 1)
    for n in pages_list:
        url = 'https://www.ximalaya.com/revision/search?core=album&kw=' + name + \
            '&page=' + str(n) + '&spellchecker=true&rows=20&condition=relation&device=iPhone'
        # print(url)
        html = requests.get(url, headers=headers)
        all = json.loads(html.text)
        data = all['data']['result']['response']['docs']
        # print(data)
        for x in data:
            title = x['title']
            id = x['id']
            treeview_album.insert('', 'end', values=(title, id))
    show_status('搜索线程结束\n')


def pass_download():
    threading.Thread(target=download).start()


def open_link_button_click():
    threading.Thread(target=open_link).start()


def treeview_album_click(event):
    threading.Thread(target=solve).start()


def search_button_click():
    threading.Thread(target=search).start()


def show_status(status):
    text_status.configure(state='normal')
    text_status.insert(END, '> ' + status)
    text_status.see(END)
    text_status.configure(state='disable')


# Build GUI
windows = tk.Tk()
windows.geometry('917x564')  # +34+306
windows.title('喜马拉雅专辑下载3.0 beta  BY:Snow')
windows.resizable(0, 0)
canvas = tk.Canvas(windows, bg="white")
canvas.place(height=88, width=904, x=5, y=469)
# TODO: 进度条
label_prograss_bar = tk.Label(windows, text='进度条')
label_prograss_bar.place(height=22, width=904, x=5, y=420)
entry_search_text = ttk.Entry(windows)
entry_search_text.place(height=34, width=531, x=4, y=5)
entry_url = ttk.Entry(windows)
entry_url.place(height=34, width=531, x=4, y=42)
entry_download_dir = ttk.Entry(windows)
entry_download_dir.place(height=34, width=531, x=4, y=80)
entry_download_dir.insert(0, os.getcwd())
button1 = ttk.Button(windows, text='搜索', command=search_button_click)
button1.place(height=34, width=123, x=539, y=5)
button2 = ttk.Button(windows, text='下载选中', command=pass_download)
button2.place(height=109, width=246, x=664, y=5)
button3 = ttk.Button(windows, text='打开链接', command=open_link_button_click)
button3.place(height=34, width=123, x=539, y=43)
# TODO: 选择目录
button4 = ttk.Button(windows, text='选择目录')
button4.place(height=34, width=123, x=539, y=80)
text_status = tk.Text(windows)
text_status.place(height=88, width=904, x=5, y=469)
show_status('启动成功！\n')
# 专辑搜索结果列表
treeview_album = ttk.Treeview(windows, height=10, show="headings", columns=columns1)
treeview_album.place(height=299, width=530, x=5, y=116)
treeview_album.column("TITLE", width=330, anchor='center')  # 表示列,不显示
treeview_album.column("ID", width=200, anchor='center')
treeview_album.heading("TITLE", text="TITLE")  # 显示表头
treeview_album.heading("ID", text="ID")
treeview_album.bind('<Double-1>', treeview_album_click)
# 音频列表
listbox_audio_name = tk.Listbox(windows, selectmode=EXTENDED)
listbox_audio_name.place(height=299, width=370, x=539, y=116)
listbox_audio_url = tk.Listbox(windows)
listbox_audio_url.place(height=0, width=0, x=0, y=0)

if __name__ == '__main__':
    windows.mainloop()
