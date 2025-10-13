__all__=["inittext","p","capture","mergecolumndata","createcolumndata","replacenewdata","analydata"]

import db2text as dt
import time,copy
from pprint import pprint

def inittext(text):
    '初始化文本，保存供后续核对，处理行分隔符等'
    dt.gd.oritext=text.splitlines(False)   #保存数据供核对
    dt.gd.text=text.splitlines(False)    #初始化要处理的数据
    if text.find("\r\n")>=0:
        dt.gd.linebreak="\r\n"
    elif text.find("\r")>=0:
        dt.gd.linebreak="\r"

def p(level,fmt,*info):
    '输出级别不高于设置值的信息，级别为-1则输出到标准错误'
    if level>dt.gd.infolevel and level!=-1:return  #级别较低不输出,-1是错误输出，输出到标准错误上
    if info is None or not info:
        sinfo = time.strftime('%H:%M:%S') + "|%d: " % (level) + fmt
    else:
        sinfo=time.strftime('%H:%M:%S')+"|%d: " %(level) +fmt %(info)
    if level>=0:
        print(sinfo)
    else:
        sys.stderr.write(sinfo+"\n")

def capture(thead,ttail):
    '在dt.gd.text里查找数据，找到则设置开始和结束位置，找不到设置开始位置为文档结尾'
    dt.gd.capturenothing=False
    for i in range(len(dt.gd.text)-len(thead)-len(ttail)):
        for j in range(len(thead)):  #依次比较头部
            if not dt.gd.text[i+j].startswith(thead[j]):
                break
        else:   #头部比较完成
            for j in range(i+len(thead)+1,len(dt.gd.text)-len(ttail)+1):
                for k in range(len(ttail)): #依次检查是否尾部
                    if not dt.gd.text[j+k].startswith(ttail[k]):
                        break
                else:   #头、尾都符合，是最终结果
                    dt.gd.capturebegin=i
                    dt.gd.captureend=j+len(ttail)-1
                    return
    dt.gd.capturebegin=len(dt.gd.text)
    dt.gd.captureend=len(dt.gd.text)
    dt.gd.capturenothing=True

def analydata():
    '根据预定义表头，解析数据成字典放在在capturedata中'
    dt.gd.capturedata={}
    if dt.gd.capturenothing:
        return
    oldtitle=[]
    for i in range(dt.gd.capturebegin,dt.gd.captureend):    #查找标题行，识别markdown和wiki格式
        if (dt.gd.text[i].startswith("|") and dt.gd.text[i].endswith("|")) or dt.gd.text[i][0]=="!":
            oldtitle=dt.gd.text[i].replace("!","|").replace("||","|").split("|")   #markdown和wiki加工成类似的数据
            oldtitle=oldtitle[1:]
            break
    if len(oldtitle)==0:   #没找到正确的标题头
        return
    columnname=""   #对应name的标题头，用来做数据的键值
    for j in dt.gd.deftitle.split():
        cname,tname=j.split(":")
        if cname=="name":
            columnname=tname
            break
    if not columnname:
        return
    titlecount=len(oldtitle)
    keynum=-1   #记录字段名对应的列序号
    for i in range(len(oldtitle)):
        if oldtitle[i].strip()==columnname:
            keynum=i
            break
    if keynum==-1:
        return
    for i in range(dt.gd.capturebegin,dt.gd.captureend):
        t=dt.gd.text[i].replace("!","|").replace("||","|").split("|")   #markdown和wiki加工成类似的数据
        if len(t)<titlecount+1:
            continue
        t=t[1:]
        dt.gd.capturedata[t[keynum].strip()]={}
        for j in range(len(oldtitle)):
            dt.gd.capturedata[t[keynum].strip()][oldtitle[j].strip()]=t[j].strip()

def mergecolumndata(t):
    '''用于markdown和wiki等，合并计算最终的用于生成表格数据的列表
'''
    retdata=[]  #返回结果
    for i in t["md"]:   #数据以capturedata为初始值，因为这里可能有字段是用户设置，并非从数据库中获取
        rowdata=copy.deepcopy(dt.gd.capturedata.get(i["name"],{}))
        retdata.append(rowdata | i)
    return retdata

def createcolumndata(mdata):
    '根据最终的列表数据，按deftitle规定的格式生成按顺序的列表数据'
    retdata=[]
    for i in mdata:
        rowdata=[]
        for j in dt.gd.deftitle.split():
            cname,tname=j.split(":")
            rowdata.append(i.get(cname,i.get(tname,"")) or "")
        retdata.append(rowdata)
    return retdata

def replacenewdata(newdata):
    '用新数据替换掉text中的相应部分'
    dt.gd.text=dt.gd.text[:dt.gd.capturebegin]+newdata+dt.gd.text[dt.gd.captureend+1:]
