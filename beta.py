# -*- coding:utf-8 -*-
from tkinter import END
from tkinter import EXTENDED
from tkinter import filedialog
from tkinter import ttk
from url_normalize import url_normalize
from urllib import parse
import json
import os
import requests
import collections
import threading
import tkinter as tk

http_headers = {
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/72.0.3626.96 Safari/537.36')}
Audio = collections.namedtuple('Audio', ['name', 'url_m4a', 'url_mp3'])
audio_format_options = ['m4a', 'mp3']

list_audio = []


def form_album_url(album_id, page_id=1, page_size=20, device='iPhone'):
    return 'http://180.153.255.6/mobile/v1/album/track/ts-1534855383505?albumId=' + album_id + \
        '&device=' + str(device) + '&isAsc=true&isQueryInvitationBrand=true&pageId=' + \
        str(page_id) + '&pageSize=' + str(page_size) + '&pre_page=0'


def form_search_url(keyword, page_id=1, device='iPhone'):
    return 'https://www.ximalaya.com/revision/search?core=album&kw=' + keyword + \
        '&page=' + str(page_id) + \
        '&spellchecker=true&rows=20&condition=relation&device=' + str(device)


def resolve_album(album_id, page_size=20):
    show_status('解析线程开始')

    url = form_album_url(album_id, page_size=page_size)
    html = requests.get(url)
    all = json.loads(html.text)
    max_page_id = all['data']['maxPageId']
    # total_counts = all['data']['totalCount']
    # last_page_totals = int(total_counts) % page_size
    list_audio.clear()
    for n in range(1, max_page_id + 1):
        url = form_album_url(album_id, page_id=n, page_size=page_size)
        html = requests.get(url)
        all = json.loads(html.text)
        data = all['data']['list']
        for a in data:
            audio = Audio(name=a['title'], url_mp3=a['playUrl64'], url_m4a=a['playPathAacv224'])
            list_audio.append(audio)
            listbox_audio.insert(END, audio.name)

    show_status('解析线程结束')


def open_link():
    listbox_audio.delete(0, END)
    album_id = url_normalize(entry_url.get()).rstrip('/').rsplit('/', 1)[-1]
    if not album_id.isdigit():
        show_status('[ERROR] 专辑链接错误')
        return
    resolve_album(album_id)
    show_status('打开专辑链接成功')


def download():
    path = entry_download_dir.get()
    if not os.path.isdir(path):
        os.makedirs(path)
    selected_indexes = listbox_audio.curselection()
    if not selected_indexes:
        return
    show_status('' + str(len(selected_indexes)) + '个任务正在下载')
    for n in range(0, len(selected_indexes)):
        audio = list_audio[int(selected_indexes[n])]
        file_name = path + '/' + audio.name + '.' + variable_audio_format.get()
        url = audio.url_m4a if variable_audio_format.get() == 'm4a' else audio.url_mp3
        response = requests.get(url, headers=http_headers)
        with open(file_name, 'wb') as code:
            code.write(response.content)
        show_status('[' + file_name + '] 下载成功')


def open_album():
    if not treeview_album.selection():
        return
    listbox_audio.delete(0, END)
    for item in treeview_album.selection():
        item_text = treeview_album.item(item, 'values')
        album_id = item_text[1]

    resolve_album(album_id)

    show_status('打开选中专辑成功')


def clear_list(tree):
    x = tree.get_children()
    for item in x:
        tree.delete(item)


def search():  # 按照关键词进行搜索
    show_status('搜索线程开始')
    clear_list(treeview_album)
    keyword = parse.quote(entry_search_text.get())
    if not keyword:
        show_status('[ERROR] 请输入关键词')
        return
    url = form_search_url(keyword)
    html = requests.get(url, headers=http_headers)
    all = json.loads(html.text)
    # docs = all['data']['result']['response']['docs']
    total_pages = all['data']['result']['response']['totalPage']
    for n in range(1, total_pages + 1):
        url = form_search_url(keyword, page_id=n)
        html = requests.get(url, headers=http_headers)
        all = json.loads(html.text)
        data = all['data']['result']['response']['docs']
        for x in data:
            title = x['title']
            id = x['id']
            treeview_album.insert('', 'end', values=(title, id))
    show_status('搜索线程结束')


def download_button_click():
    threading.Thread(target=download).start()


def open_link_button_click():
    threading.Thread(target=open_link).start()


def treeview_album_click(event):
    threading.Thread(target=open_album).start()


def search_button_click():
    threading.Thread(target=search).start()


def select_dir_button_click():
    download_dir = filedialog.askdirectory()
    entry_download_dir.delete(0, END)
    entry_download_dir.insert(0, download_dir)


def show_status(status):
    text_status.configure(state='normal')
    text_status.insert(END, '> ' + status + '\n')
    text_status.see(END)
    text_status.configure(state='disable')


if __name__ == '__main__':
    # Build GUI
    window = tk.Tk()
    window.geometry('917x564')  # +34+306
    window.title('喜马拉雅专辑下载, Originally by Snow')
    window.resizable(0, 0)
    canvas = tk.Canvas(window, bg='white')
    canvas.place(height=88, width=904, x=5, y=469)
    # TODO: 进度条
    label_prograss_bar = tk.Label(window, text='进度条')
    label_prograss_bar.place(height=22, width=904, x=5, y=420)
    entry_search_text = ttk.Entry(window)
    entry_search_text.place(height=34, width=531, x=4, y=5)
    entry_url = ttk.Entry(window)
    entry_url.place(height=34, width=531, x=4, y=42)
    entry_download_dir = ttk.Entry(window)
    entry_download_dir.place(height=34, width=531, x=4, y=80)
    entry_download_dir.insert(0, os.getcwd())
    button1 = ttk.Button(window, text='搜索', command=search_button_click)
    button1.place(height=34, width=123, x=539, y=5)
    button2 = ttk.Button(window, text='下载选中', command=download_button_click)
    button2.place(height=77, width=246, x=664, y=5)
    button3 = ttk.Button(window, text='打开链接', command=open_link_button_click)
    button3.place(height=34, width=123, x=539, y=43)
    button4 = ttk.Button(window, text='选择目录', command=select_dir_button_click)
    button4.place(height=34, width=123, x=539, y=80)

    label_audio_format = tk.Label(window, text='音频格式')
    label_audio_format.place(height=40, width=123, x=664, y=82)
    variable_audio_format = tk.StringVar(window)
    option_menu_audio_format = ttk.OptionMenu(
        window, variable_audio_format, audio_format_options[0], *audio_format_options)
    option_menu_audio_format.place(height=40, width=123, x=787, y=82)

    text_status = tk.Text(window)
    text_status.place(height=88, width=904, x=5, y=469)

    column_headers = ('TITLE', 'ID')
    treeview_album = ttk.Treeview(window, height=10, show='headings', columns=column_headers)
    treeview_album.place(height=299, width=530, x=5, y=116)
    treeview_album.column(column_headers[0], width=330, anchor='center')
    treeview_album.column(column_headers[1], width=200, anchor='center')
    treeview_album.heading(column_headers[0], text='专辑名')
    treeview_album.heading(column_headers[1], text='专辑编号')
    treeview_album.bind('<Double-1>', treeview_album_click)

    listbox_audio = tk.Listbox(window, selectmode=EXTENDED)
    listbox_audio.place(height=299, width=370, x=539, y=116)

    show_status('启动成功')
    window.mainloop()
