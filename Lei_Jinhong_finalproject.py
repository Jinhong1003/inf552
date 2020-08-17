import requests
from bs4 import BeautifulSoup
import re
import argparse
import sqlite3
##import matplotlib.font_manager as fm
##from matplotlib.ft2font import FT2Font
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import csv

def parse_args():
        description = "you should add those parameter"
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-source',choices=["local","remote","test"],nargs=1,
                            help='where data should be gotten from')

        args = parser.parse_args()
        location=args.source
        
        return location


####scrape data######
def findUrl(url):
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            soup= None
            return soup
        else:
            print(f"{r.url} was successfully retrieved with status code{r.status_code}")
            soup = BeautifulSoup(r.content, 'lxml')
            return soup
        
def scrapename():
    wholelist=[]    
    for i in range(1,6):
        url=f"https://musicbrainz.org/series/b3484a66-a4de-444d-93d3-c99a73656905?page={i}"
        soup=findUrl(url)
        if soup == None:
            break 
        main_table=soup.findAll("body")[0]
        a=main_table.find("tbody")
        b=a.findAll("tr")
        for items in b:
            pairlist=[]
            song_name=items.findAll("td")[1].find("bdi").contents[0]
            singer_name=items.findAll("td")[2].find("bdi").contents[0]
            pairlist.append(singer_name)
            pairlist.append(song_name)
            wholelist.append(pairlist)
    return(wholelist)

def scrapenamefortest():
    wholelist=[]    
    for i in range(1,3):
        url=f"https://musicbrainz.org/series/b3484a66-a4de-444d-93d3-c99a73656905?page={i}"
        soup=findUrl(url)
        if soup == None:
            break 
        main_table=soup.findAll("body")[0]
        a=main_table.find("tbody")
        b=a.findAll("tr")
        for items in b:
            pairlist=[]
            song_name=items.findAll("td")[1].find("bdi").contents[0]
            singer_name=items.findAll("td")[2].find("bdi").contents[0]
            pairlist.append(singer_name)
            pairlist.append(song_name)
            wholelist.append(pairlist)
    return(wholelist)




def scrape_common_words():
    top100list=[]
    url="https://en.wikipedia.org/wiki/Most_common_words_in_English"
    soup=findUrl(url)
    if soup==None:
        return (None)
    main_table=soup.findAll("body")[0]
    a=main_table.find("tbody")
    b=a.findAll("a",{"class" : "extiw"})
    for items in b:
        word=items.attrs["title"][5:]
        top100list.append(word)
    return(top100list)


def decontracted(phrase):
    # specific
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can't", "can not", phrase)
    phrase = re.sub(r"don't", "do not", phrase)
    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)  
    return phrase


    
def lyrics():
    lyriclist=[]
    for items in wholelist:
        url=f'https://api.lyrics.ovh/v1/{items[0]}/{items[1]}'
        soup=findUrl(url)
        if soup==None:
            continue
        main_table=soup.findAll("body")[0].find("p").contents[0]
        lyrics=main_table[11:(len(main_table)-2)]
        lyrics=lyrics.lower()
        lyrics=decontracted(lyrics)

        a=lyrics.split()
        b=[]
        for items in a:
            if "\\n" in items:
                c=items.split("\\n" )
                for i in range(len(c)):
                    lyriclist.append(c[i])
            else:
                lyriclist.append(items)
        for items in b:
            if items=="":
                lyriclist.remove(items)
    return lyriclist

def lyricdic(a):
    dic={}
    for items in a:
        if items not in dic:
            dic[items]=1
        else:
            dic[items]+=1
    return dic

def lyric_common_words(a):
    dic=a
    if "" in dic:
        del dic[""]
    b=sorted(dic.items(),key=lambda item:item[1])[-100:-1]
    b.append(sorted(dic.items(),key=lambda item:item[1])[-1])
    return b


#### saving data#####
def creatdatabase():
    conn = sqlite3.connect('Allwords.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE song500list (song_id int,singer_name string ,song_name string)")
    cur.execute("CREATE TABLE top100wordlist (commonword_id int,common_word string)")
    cur.execute("CREATE TABLE lyric_common_wordlist (lyric_word_rank_id int, lyric_word string,times int)")


def insert_song500list():
    conn = sqlite3.connect('Allwords.db')
    cur = conn.cursor()
    a=0
    for i in range(len(wholelist)):
        cur.execute(f'''SELECT * FROM song500list WHERE singer_name="{wholelist[i][0]}" AND song_name=="{wholelist[i][1]}"''')
        entry = cur.fetchone()
        if entry is None:
            cur.execute('INSERT INTO song500list (song_id,singer_name,song_name) VALUES (?,?,?)', (a,wholelist[i][0],wholelist[i][1]))
            a=a+1
            print('New entry added')
        else:
            print ('Entry found')
    conn.commit()

def insert_top100wordlist():
    conn = sqlite3.connect('Allwords.db')
    cur = conn.cursor()
    a=0
    for i in range(len(top100list)):
        cur.execute(f'''SELECT * FROM top100wordlist WHERE common_word="{top100list[i]}"''')
        entry = cur.fetchone()
        if entry is None:
            cur.execute('INSERT INTO top100wordlist (commonword_id,common_word) VALUES (?,?)', (a,top100list[i]))
            a=a+1
            print('New entry added')
        else:
            print ('Entry found')
    conn.commit()

def insert_lyric_common_wordlist():
    conn = sqlite3.connect('Allwords.db')
    cur = conn.cursor()
    a=0
    for i in range(len(lyric_common_words)):
        cur.execute(f'''SELECT * FROM lyric_common_wordlist WHERE lyric_word="{lyric_common_words[i][0]}" AND times="{lyric_common_words[i][1]}" ''')
        entry = cur.fetchone()
        if entry is None:
            cur.execute('INSERT INTO lyric_common_wordlist (lyric_word_rank_id,lyric_word, times) VALUES (?,?,?)',(a,lyric_common_words[i][0],lyric_common_words[i][1]))
            a=a+1
            print('New entry added')
        else:
            print ('Entry found')
    conn.commit()

#####visualization    
def makebarchart():
        conn = sqlite3.connect('Allwords.db')
        cur = conn.cursor()
        a=cur.execute("""
                        SELECT lyric_word From lyric_common_wordlist
                        """).fetchall()
        b=cur.execute("""
                        SELECT times From lyric_common_wordlist
                        """).fetchall()
        c=cur.execute("""
                        SELECT lyric_word From lyric_common_wordlist
                        LIMIT 20
                        """).fetchall()
        d=cur.execute("""
                        SELECT times From lyric_common_wordlist
                        LIMIT 20
                        """).fetchall()
##        print(c)
##        for items in c:
##                print (items[0])
        
##        fig = plt.figure()
##        plt.bar(a,b,1,color="green")
##        plt.xlabel("X-axis")
##        plt.ylabel("Y-axis")
##        plt.title("bar chart")
        
##        labels=list(range(100))
        e=[]                  
        for items in b:
            e.append(items[0])
        plt.xlabel("rank_popular_lyric_words")
        plt.ylabel("times_in_song")
        plt.title("top 100 popular lyric words bar chart")
        plt.bar(range(len(e)),e,fc="r")
        plt.show()
        
        f=[]
        g=[]
        for items in c:
                g.append(items[0])
        labels = g
        for items in d:
            f.append(items[0])
        plt.xlabel("popular_lyric_words")
        plt.ylabel("times_in_song")
        plt.title("top 20 popular lyric words bar chart")
        plt.bar(range(len(f)),f,tick_label=labels)
        plt.show()
##        plt.savefig("baaaaaaa.jpg")
        
def makepiechart():
        conn = sqlite3.connect('Allwords.db')
        cur = conn.cursor()           
        c=cur.execute("""
                        SELECT common_word FROM top100wordlist
                        WHERE  common_word IN
                        (SELECT lyric_word From lyric_common_wordlist)
                                """).fetchall()
        d=len(c)
        labels=['popular_lyric_word','not_popular_lyric_word']
        X=[d,100-d]
        fig = plt.figure()
        plt.pie(X,labels=labels,autopct='%1.2f%%')
        plt.title("Pie chart of common words")
        plt.show() 
def makeScatterplot():
        conn = sqlite3.connect('Allwords.db')
        cur = conn.cursor()
        
        a=cur.execute("""
                        SELECT common_word FROM top100wordlist
                        WHERE  common_word IN
                        (SELECT lyric_word From lyric_common_wordlist)
                        """).fetchall()
        b=cur.execute("""
                        SELECT * FROM lyric_common_wordlist
                        """).fetchall()
        c={}
        d=[]
        e=[]
        for items in a:
                d.append(items[0])
        for items in b:
                c[items[1]]=items[2]
        for items in d:
                e.append(c[items])
                
##        print(d)
##        print(c)
##        print(e)

        plt.title("scatter diagram of common words appears in popular lyric") 
        plt.plot(d,e,'ro')
        plt.show()

        
##        b=cur.execute("""
##                        SELECT times FROM lyric_common_wordlist
##                        WHERE  lyric_common_wordlist.lyric_word IN
##                        (SELECT common_word FROM top100wordlist
##                        WHERE  common_word IN
##                        (SELECT lyric_word From lyric_common_wordlist))                        
##                        """).fetchall()
##        c=cur.execute("""
##                        SELECT common_word FROM top100wordlist
##                        """).fetchall()        

##        print(c)
def result():
        print("____________________________________result______________________________________")
        print("There are three kinds of pictures in my project,including bar,pie and scatters.")
        print("According to the visualization we have done,there are 64% of common words are \npopular lyrics,and the more popular lyric it is the more common words it belongs to.") 
        print("In conclusion,song writers should right the song use the word as common as \npossible so that the song will be easier to become popular and great!")
        print("________________________________________________________________________________")
def showoutput():
        a=input("please input the kind of output you want \n (bar chart/pie chart/scatter plot/conclusion/all/quit):")
        if a=="bar chart":
            makebarchart()
            showoutput()
        elif a=="pie chart":
            makepiechart()
            showoutput()
        elif a=="scatter plot":
            makeScatterplot()
            showoutput()
        elif a=="conclusion":
            result()
            showoutput()
        elif a=="all":
            makebarchart()
            makepiechart()
            makeScatterplot()
            result()
            showoutput()
        elif a=="quit":
            pass
        else:
            print("please re-run the code use the correct parameters")

def cleandata():
    a=[]
    with open("data.csv",'r') as b:
            reader=csv.reader(b)
            for lines in reader:
                a.append(lines)
    for items in a[2]:
        if items=='("\'cause", 191)':
             a[2].remove(items)
    a[2].append("('cause', 191)")
    return (a)
def gettop100list(a):
    top100list=a[1]
    return(top100list)
def getlyric_common_words(a):
    lyric_common_words=[]
    for items in a[2]:
        b=[]
        splititems1=items.split(",")
        if len(splititems1[1])==1:
            splititems1[1]=splititems1[2]
        b.append(splititems1[0][2:-1])
        b.append(splititems1[1][1:-1])
        lyric_common_words.append(b)
    return(lyric_common_words)


if __name__ == '__main__':
#        args = parse_args()
        location=parse_args()
#        if args.remote:
        if location==["remote"]:
                wholelist=scrapename() ### 500songlist
                top100list=scrape_common_words()
                lyriclist=lyrics()
                lyricdic=lyricdic(lyriclist)
         #       lyric_common_words(lyricdic).reverse()
                lyric_common_words=lyric_common_words(lyricdic)
                lyric_common_words.reverse()
                print(wholelist)
                print(top100list)
                print(lyric_common_words)
                
                a=[]

                with open("data.csv",'w') as f:
                        writer=csv.writer(f)
                        writer.writerow(wholelist)
                        writer.writerow(top100list)
                        writer.writerow(lyric_common_words)


                with open("data.csv",'r') as b:
                        reader=csv.reader(b)
                        for lines in reader:
                            a.append(lines)
                for items in a[2]:
                    if items=='("\'cause", 191)':
                         a[2].remove(items)
                a[2].append("('cause', 191)")

                                
                wholelist=[]
                top100list=a[1]
                lyric_common_words=[]
                for items in a[2]:
                    b=[]
                    splititems1=items.split(",")
                    if len(splititems1[1])==1:
                        splititems1[1]=splititems1[2]
                    b.append(splititems1[0][2:-1])
                    b.append(splititems1[1][1:-1])
                    lyric_common_words.append(b)

                for items in a[0]:
                    d=[]
                    e=[]
                    splititems2=items.split(",")
                    b=splititems2[0][2:-1]
                    c=splititems2[1][2:-2]
                    e.append(c)
                    d.append(b)
                    d.append(e)
                    wholelist.append(d)                
                creatdatabase()
#                insert_song500list()
                insert_top100wordlist()
                insert_lyric_common_wordlist()
                conn = sqlite3.connect('Allwords.db')
                cur = conn.cursor()
                cur.execute("""
                                SELECT lyric_word From lyric_common_wordlist

                                """)
                a=cur.fetchall()
                b=cur.execute("""
                                 SELECT times From lyric_common_wordlist

                                """).fetchall()
                c=cur.execute("""
                                SELECT common_word FROM top100wordlist
                                WHERE  common_word IN
                                (SELECT lyric_word From lyric_common_wordlist)
                                """).fetchall()






                conn = sqlite3.connect('Allwords.db')
                cur = conn.cursor()
                cur.execute("""
                                SELECT lyric_word From lyric_common_wordlist

                                """)
                a=cur.fetchall()
                b=cur.execute("""
                                 SELECT times From lyric_common_wordlist

                                """).fetchall()
                c=cur.execute("""
                                SELECT common_word FROM top100wordlist
                                WHERE  common_word IN
                                (SELECT lyric_word From lyric_common_wordlist)
                                """).fetchall()
                d=len(c)
                labels=['popular_lyric_word','not_popular_lyric_word']
                X=[d,100-d]
                fig = plt.figure()
                plt.pie(X,labels=labels,autopct='%1.2f%%')
                plt.title("Pie chart of common words")
                
                plt.show() 

                c=[]                  
                for items in b:
                        c.append(items[0])
                plt.bar(range(len(c)), c)
                plt.show()
#                print("local")


                
#        elif args.local:
        elif location==["local"]:
                a=cleandata()

                top100list=gettop100list(a)
                lyric_common_words=getlyric_common_words(a)

##                a=[]
##                
##                with open("data.csv",'r') as b:
##                        reader=csv.reader(b)
##                        for lines in reader:
##                            a.append(lines)
##                for items in a[2]:
##                    if items=='("\'cause", 191)':
##                         a[2].remove(items)
##                a[2].append("('cause', 191)")
##
##                                
##                wholelist=[]
##                top100list=a[1]
##                lyric_common_words=[]
##                for items in a[2]:
##                    b=[]
##                    splititems1=items.split(",")
##                    if len(splititems1[1])==1:
##                        splititems1[1]=splititems1[2]
##                    b.append(splititems1[0][2:-1])
##                    b.append(splititems1[1][1:-1])
##                    lyric_common_words.append(b)

##                for items in a[0]:
##                    d=[]
##                    e=[]
##                    splititems2=items.split(",")
##                    b=splititems2[0][2:-1]
##                    c=splititems2[1][2:-2]
##                    e.append(c)
##                    d.append(b)
##                    d.append(e)
##                    wholelist.append(d)
                try:
                        creatdatabase()
        #                insert_song500list()
                        insert_top100wordlist()
                        insert_lyric_common_wordlist()
                        showoutput()
                                
                except:
                        showoutput()

                
                    
                
##                conn = sqlite3.connect('Allwords.db')
##                cur = conn.cursor()
##                a=cur.execute("""
##                                SELECT * From lyric_common_wordlist
##
##                                """).fetchall()
##                b=cur.execute("""
##                                 SELECT * From top100wordlist
##
##                                """).fetchall()
##                c=cur.execute("""
##                                 SELECT * From song500list
##
##                                """).fetchall()
##                print(a)
##                print(b)
##                print(c)
##
##                
##                a=cur.execute("""
##                                SELECT lyric_word From lyric_common_wordlist
##
##                                """).fetchall()
##               
##                b=cur.execute("""
##                                 SELECT times From lyric_common_wordlist
##
##                                """).fetchall()
##         
##                c=cur.execute("""
##                                SELECT common_word FROM top100wordlist
##                                WHERE  common_word IN
##                                (SELECT lyric_word From lyric_common_wordlist)
##                                """).fetchall()
##  
##                d=len(c)
##                labels=['popular_lyric_word','not_popular_lyric_word']
##                X=[d,100-d]
##                fig = plt.figure()
##                plt.pie(X,labels=labels,autopct='%1.2f%%')
##                plt.title("Pie chart of common words")
##                
##                plt.show() 
## #               plt.rcParams['font.sans-serif']=['SimHei']
## #               plt.figure(figsize=(6,9)) #调节图形大小
## #               labels = [u'大型',u'中型'] #定义标签
## #               sizes = [100-d,d] #每块值
## #               colors = ['red','yellowgreen'] #每块颜色定义
## #               explode = (0,0,) #将某一块分割出来，值越大分割出的间隙越大
## #               patches,text1,text2 = plt.pie(sizes,
## #                                     explode=explode,
## #                                     labels=labels,
## #                                     colors=colors,
## #                                     autopct = '%3.2f%%', #数值保留固定小数位
## #                                     shadow = False, #无阴影设置
## #                                     startangle =90, #逆时针起始角度设置
## #                                     pctdistance = 0.6) #数值距圆心半径倍数距离
##                #patches饼图的返回值，texts1饼图外label的文本，texts2饼图内部的文本
##                # x，y轴刻度设置一致，保证饼图为圆形
## #               plt.axis('equal')
## #               plt.show()
##
##                c=[]                  
##                for items in b:
##                        c.append(items[0])
##                plt.bar(range(len(c)), c)
##                plt.show()
 #               print("local")
        elif location==["test"]:
                wholelist=scrapenamefortest() ### 200songlist
                top100list=scrape_common_words()
                lyriclist=lyrics()
                lyricdic=lyricdic(lyriclist)
   #             lyric_common_words(lyricdic).reverse()
                lyric_common_words=lyric_common_words(lyricdic)
                lyric_common_words.reverse()
                print(wholelist)
                print(top100list)
                print(lyric_common_words)


                a=[]

                with open("data.csv",'w') as f:
                        writer=csv.writer(f)
                        writer.writerow(wholelist)
                        writer.writerow(top100list)
                        writer.writerow(lyric_common_words)
                with open("data.csv",'r') as b:
                        reader=csv.reader(b)
                        for lines in reader:
                                a.append(lines)
 
                for items in a[2]:
                    if items=='("\'cause", 191)':
                         a[2].remove(items)
                a[2].append("('cause', 191)")

                                
                wholelist=[]
                top100list=a[1]
                lyric_common_words=[]
                for items in a[2]:
                    b=[]
                    splititems1=items.split(",")
                    if len(splititems1[1])==1:
                        splititems1[1]=splititems1[2]
                    b.append(splititems1[0][1:])
                    b.append(splititems1[1][1:-1])
                    lyric_common_words.append(b)
                for items in a[0]:
                    d=[]
                    splititems2=items.split(",")
                    b=splititems2[0][2:-1]
                    c=splititems2[1][:-1]
                    d.append(b)
                    d.append(c)
                    wholelist.append(d)

                    
                                
                creatdatabase()
                insert_song500list()
                insert_top100wordlist()
                insert_lyric_common_wordlist()
                conn = sqlite3.connect('Allwords.db')
                cur = conn.cursor()
                cur.execute("""
                                SELECT lyric_word From lyric_common_wordlist

                                """)
                a=cur.fetchall()
                b=cur.execute("""
                                 SELECT times From lyric_common_wordlist

                                """).fetchall()
                c=cur.execute("""
                                SELECT common_word FROM top100wordlist
                                WHERE  common_word IN
                                (SELECT lyric_word From lyric_common_wordlist)
                                """).fetchall()






                conn = sqlite3.connect('Allwords.db')
                cur = conn.cursor()
                cur.execute("""
                                SELECT lyric_word From lyric_common_wordlist

                                """)
                a=cur.fetchall()
                b=cur.execute("""
                                 SELECT times From lyric_common_wordlist

                                """).fetchall()
                c=cur.execute("""
                                SELECT common_word FROM top100wordlist
                                WHERE  common_word IN
                                (SELECT lyric_word From lyric_common_wordlist)
                                """).fetchall()
                d=len(c)
                labels=['popular_lyric_word','not_popular_lyric_word']
                X=[d,100-d]
                fig = plt.figure()
                plt.pie(X,labels=labels,autopct='%1.2f%%')
                plt.title("Pie chart of common words")
                
                plt.show() 

                c=[]                  
                for items in b:
                        c.append(items[0])
                plt.bar(range(len(c)), c)
                plt.show()
                
                
        else:
                print("please re-run the code use the correct parameters")
