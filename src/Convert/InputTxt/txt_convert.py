#!/usr/bin/env python
#需要python 3环境
import sys
import chardet  ##这个库需要另外下载
import optparse
import os
import codecs
import re

class Paragraph:
    def __init__(self):
        self.setC("")
        self.setContent("")

    def setC(self,c):
        self.c = c

    def getC(self):
        return self.c
    
    def showC(self):
        print(self.c)

    def setContent(self,string):
        self.content = string

    def getContent(self):
        return self.content

    def showContent(self):
        print(self.content)

    def cleanContent(self):
        self.content = self.content.replace("&","&amp;")
        self.content = self.content.replace("<","&lt;")
        self.content = self.content.replace(">","&gt;")
        return
        
class Text:
##    def parseline(self,file,charset):
##        if (charset.lower() == 'gbk'):
##            plt = file.readline().decode(encoding = "gbk")
##        if (charset.lower() == 'utf-8'):
##            plt = file.readline().decode(encoding = "utf-8",errors = "ignore")
##        return plt
            
    def __init__(self,path = 0,mode = 1,charset = 'gbk'):
        if (path == 0):
            self.setPosition(0)
            self.p_number = 0
            self.para = []
        else:
            self.setPosition(0)
            self.p_number = 0
            self.para = []

            print("charset:"+charset)
            book = open(path,'r+',encoding = charset,errors = "ignore")
            temp = book.readline()                    
            print(type(temp))
            while temp:
                p = Paragraph()
                p.setContent(temp)
                p.setC("p")
                self.newPara(p,1)
                temp = book.readline()
            book.close()
            return

    def newPara(self,para,convert):###convert  = 1去除空行
        if (convert == 1)and(para.getContent() != '\n'):
            self.para.append(para)
        elif (convert == 0):
            self.para.append(para)

    def showallPara(self):
        for paragraph in self.para:
            paragraph.showContent()

    def showPara(self):
        self.para[self.pos].showContent()
        self.pos = self.pos + 1

    def getPara(self):
        if self.getPosition() < len(self.para):
            t = self.para[self.pos]
            self.pos = self.pos + 1
            return t
        else:
            self.pos = self.pos + 1
            return -1
    def previousPara(self):
        if self.getPosition() > 0:
            return self.para[self.getPosition() - 2]
        else:
            return -1
    def ppreviousPara(self):
        if self.getPosition() > 0:
            return self.para[self.getPosition() - 3]
        else:
            return -1

    def delPara(self,n):
        del self.para[n]
        if self.getPosition() >= n:
            self.setPosition(self.getPosition() - 1)

    def insertPara(self,n):
        p = Paragraph()
        self.para.insert(n,p)
        if self.getPosition() >=n:
            self.setPosition(self.getPosition() + 1)
        return p
        
    def setPosition(self,n):
        if (type(n) == int):
            self.pos = n
            
    def getPosition(self):
        
        return (self.pos)

    def makeText(self,path):
        t = open(path,'w+',encoding = "utf-8")
        self.setPosition(0)
        while (self.getPosition() < len(self.para) - 1):
            t.write(self.getPara().getContent())
        t.close()

    def clear(self):
        self.setPosition(0)
        p = self.getPara()
        while (type(p) == Paragraph):
            if p.getC() == 'd':
                self.delPara(self.getPosition()-1)
            p = self.getPara()
        return

    def makeHtml(self,path):
        f = open(path,'w+',encoding = 'utf-8')
        self.setPosition(0)
        p = self.getPara()
        f.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">\n')
        f.write('\t<head>\n')
        f.write('\t\t<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n')
        f.write('\t\t<title>' + 'noname' + '</title>\n')
        f.write('\t</head>\n\n\t<body>\n')
        f.write('\t\t<h1>﻿</h1>\n')
        while (p != -1):
            if p.getC() == 'h2':
                f.write('\t\t<h2>' + p.getContent()[:-1] + '</h2>\n')
            if p.getC() == 'p':
                f.write('\t\t<p>' + p.getContent()[:-1] + '</p>\n')
            p = self.getPara()
        f.write('\n\n\t</body>\n</html>')
        f.close()

    def structuredetect(self):
        self.setPosition(0)
        p = self.getPara()
        while type(p) == Paragraph:
            string = p.getContent()
            #z1 = re.compile('[第]{1}[一二三四五六七八九十百千]{1,7}[章部节卷篇]{1}[ 　]+')
            z1 = re.compile('[第]{1}[零一二三四五六七八九十百千1234567890]{1,7}[章部节卷篇]{1}[\s 　：]?')
            #z2 = re.compile('[第]{1}[1234567890]{1,5}[章部节卷篇]{1}[\s　]+')
            #z2 = re.compile('[第]{1}[1234567890]{1,5}[章部节卷篇]{1}[\s　：]+')
            z3 = re.compile('[第]{1}[零一二三四五六七八九十百千0123456789]{1,7}[章部节卷篇]{1}[\s 　：]?\S{1,20}[\s 　：]?[第]{1}[零一二三四五六七八九十百千0123456789]{1,7}[章部节卷篇]{1}[\s 　：]?\S{1,20}[\s 　：]+')
            z4 = re.compile('[。]{1}')   ###标题一般不包含句号
            if str(type(re.match(z1,string))) != "<class 'NoneType'>":
                p.setC('h2')
            elif str(type(re.search(z1,string))) != "<class 'NoneType'>"and str(type(re.search(z4,string))) == "<class 'NoneType'>"and len(string) < 30:
                p.setC('h2')
            #if p.getC() != 'h2':
                #if str(type(re.match(z2,string))) != "<class 'NoneType'>":
                    #p.setC('h2')
                #elif str(type(re.search(z2,string))) != "<class 'NoneType'>"and string.find('第') <3:
                    #p.setC('h2')
            if p.getC() != 'h2':
                if str(type(re.match(z3,string))) != "<class 'NoneType'>":
                    p.setC('h2')
                elif str(type(re.search(z3,string))) != "<class 'NoneType'>"and str(type(re.search(z4,string))) == "<class 'NoneType'>"and len(string) < 30:
                    p.setC('h2')
            if p.getC() == 'h2':
                pt = re.findall('[章部节卷篇]{1}[\s　：]?\S+[\s　：]+',string)
                if (len(pt) != 0):
                    x = len(pt)-1
                    s = string.find(pt[x]) + len(pt[x])
                    if (len(string) > s + 5):
                        p.setContent(string[:s])
                        p2 = self.insertPara(self.getPosition())
                        p2.setContent(string[s:])
                        p2.setC('p')

            if p.getC() == 'h2':
                if self.previousPara().getC() == 'h2':
                    self.previousPara().setC('d')
                elif type(self.ppreviousPara()) == Paragraph:
                    if self.ppreviousPara().getC() == 'h2':
                        self.previousPara().setC('d')
                        self.ppreviousPara().setC('d')
                        
            p = self.getPara()
        self.clear()

        return
def main():

    
    usage = "Convert txt file to xhtml and divide into chapters" 
    parser = optparse.OptionParser(usage=usage) 
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True, help="make lots of noise [default]") 
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="be quiet")
    parser.add_option("-i", "--inputfilename", action="store", type="string", dest="inputfilename", help="input txt file")
    parser.add_option("-o", "--outputfilename", action="store", type="string", dest="outputfilename", help="output epub file")  
    parser.add_option("-m", "--mode", default="1",dest="buffermode", help="buffer mode: 0 or 1 [default: %default]")
    parser.add_option("-c", "--chapter", default="1",dest="chaptermode", help="chapter mode: 0 or 1 [default: %default]")
    (options, args) = parser.parse_args() 
    if options.inputfilename and options.outputfilename:
        pass 
    else:
        parser.error("Wrong input file or output file!")
        sys.exit(1)

        
    txt = open(options.inputfilename,"rb",int(options.buffermode))
    #txt = open(r"D:\1.txt","r",1)
    
    #此处为节省内存，仅判断文章的前100000个字符
    t = txt.read(100000)
    chardict = chardet.detect(t)
    txt.close()
    
    max_key = 0
    print(chardict)
    for key in chardict.keys():
        if (key == 'encoding'):
            max_value = chardict[key]
    print(max_value)
    if (max_value == "GB2312"):
        max_value = "gbk"
    if not max_value:
        max_value = "utf-16"   
    raw_charset = max_value
    print(type(raw_charset))


    txtfile = Text(options.inputfilename,int(options.buffermode),charset = raw_charset)
    #txtfile = Text(path = r"D:\1.txt",mode = 1,charset = raw_charset)
    for p in txtfile.para:
        p.cleanContent()
    #txtfile.makeText(r"D:\2.TXT")
    if (int(options.chaptermode) == 1):
        txtfile.structuredetect()
    txtfile.makeHtml(options.outputfilename)

        
        

    

if __name__ == '__main__':
    main()
