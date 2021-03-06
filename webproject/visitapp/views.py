from django.shortcuts import render
import sqlite3
import shutil
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

# Create your views here.
def visit(request):

    homepath = os.path.expanduser("~")
    abs_chrome_path = os.path.join(homepath, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History')
    # 파일복사
    shutil.copyfile(abs_chrome_path, abs_chrome_path+"_copy")

    data_list = []
    con = sqlite3.connect(abs_chrome_path+"_copy")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM urls order by visit_count ASC")
    for row in cursor.execute("SELECT * FROM urls order by visit_count DESC limit 5"):
        data_list.append(row)
    df = pd.DataFrame(data_list, columns=['id', 'url', 'title', 'visit_count', 'typed_count', 'last_visit_time', 'hidden'])
    # print(df)
    df = df.loc[:,['url', 'title', 'visit_count']]
    df_visit_count = df.sort_values(by='visit_count', axis=0, ascending=False)
    # print(df_visit_count)
    # print(df_visit_count[:5][['url', 'visit_count']])
    count=0
    favi_list=[]
    url_list=[]
    title_list=[]
    # print('<favicon_url | url | title>')
    for name, row in df_visit_count.iterrows():
        if count==5:
            break
        url = row[0]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        link_tag = soup.select('head > link')
        if link_tag is not None:
            for link in link_tag:
    #             print(link['rel'])
                if link['rel'][0] == 'shortcut':
                    favicon_url = link['href']
        else:
            favicon_url = None
        # print(f'{favicon_url}, {row[0]}, {row[1]}')
        count+=1
        favi_list.append(favicon_url)
        url_list.append(row[0])
        title_list.append(row[1])

    con.close()
    context = {
        'favicon_url' : favi_list,
        'url_list': url_list,
        'title' : title_list
    }
    #print(context['favicon_url'])


    count=0
    title = []
    visit_count = []
    for name, row in df_visit_count.iterrows():
        if count==5:
            break
        title.append(row[1])
        visit_count.append(row[2])
        count+=1

    df = pd.DataFrame([title, visit_count], index=['title','visit_count']).T

    plt.rc('font', family='NanumGothic')
    plt.figure(figsize=(10,6))
    #plt.subplot(221)
    #plt.xticks(rotation=90)
    sns.barplot(data=df, x='visit_count', y='title')

    plt.savefig('./static/images/bar.png',dpi=300, bbox_inches='tight')

    plt.figure(figsize=(10,6))
    #plt.subplot(222)
    #plt.pie(visit_count, labels=title)
    group_explodes = (0.1, 0, 0, 0, 0)
    plt.pie(visit_count, 
            explode=group_explodes, 
            labels=title, 
            autopct='%1.2f%%', # second decimal place
            shadow=True, 
            startangle=90,
            textprops={'fontsize': 12}) # text font size
    plt.axis('equal') #  equal length of X and Y axis

    plt.savefig('./static/images/pie.png',dpi=300, bbox_inches='tight')

    return render(request, 'visitapp/visit.html', context) 