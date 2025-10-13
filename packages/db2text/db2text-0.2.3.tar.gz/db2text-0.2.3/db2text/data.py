# db2text的全局数据

__all__=["gd"]

class gd(object):   #全局数据
#以下为设置项
    coding="utf8"   #字符集，默认为utf8
    linebreak="\n"  #检测到换行符，则替换掉这个，没检测到，使用这个默认的
    infolevel=1     #设置提示信息级别
    localinfolevel=1    #局部消息级别

#以下为数据项
    oritext=[]      #保存文本的初始值
    text=[]         #保存处理后的文本
    capturebegin=0  #捕获的数据在text中的开始序号
    captureend=0  #捕获的数据在text中的结束序号
    capturedata={}  #保存捕获的数据，以字段名为键值，保存一个字典，指定一行的数据内容，键值为标题
    capturenothing=True #标记是不是捕获到
    deftitle=""     #表头，如 name:字段名 desc:注释 ts:类型 default:默认值 :说明
