import sys,datetime,time,re,pandas as pd
from IPython.display import display

# import as で名前を変えるのと同じようなもの、importのifをどう書けばよいか分かったのち対応
if hasattr(time,"time_ns"):
    def getTime():
        return time.time_ns()
else:
    def getTime():
        return int( time.monotonic() * 1000000000 )

class counter:
    instanceStack = []

    def countReset():
        counter.instanceStack.clear()
        
    def __init__(self,_max,_printWaitSec = 1,_countClear = False):
        if _countClear:
            counter.countReset()
            
        if len(counter.instanceStack) > 0:
            superCounter  = counter.instanceStack[-1]
            maxCount      = superCounter.max * _max
            stepCount     = superCounter.cnt * _max
            startTime     = superCounter.start
            displayHandle = superCounter.displayHandle
            lastTime      = superCounter.lastTime
        else:
            print("START TIME : {}{}".format(str(datetime.datetime.now())," "*60))
            displayHandle = display("time display here",display_id = True)
            print()
            maxCount      = _max
            stepCount     = 0
            startTime     = getTime()
            lastTime      = 0
            
        self.instanceCount = len(counter.instanceStack)
        counter.instanceStack.append(self)
        
        self.displayHandle = displayHandle
        self.max           = maxCount
        self.cnt           = stepCount
        self.lastTime      = lastTime
        self.printWait     = int( _printWaitSec * 1000000000 )
        self.start         = startTime
    
    def __del__(self):
        self.leaveStep()
    
    def leaveStep(self):
        if self.instanceCount > 0:
            leaveCnt = len(counter.instanceStack)-self.instanceCount
            for i in range(leaveCnt):
                counter.instanceStack.pop()
        else:
            counter.countReset()
    def checkUnder(self):
        if len(counter.instanceStack) - self.instanceCount > 1:
            leaveCnt = len(counter.instanceStack)-self.instanceCount-1
            for i in range(leaveCnt):
                counter.instanceStack.pop()
    
    def call(self):
        timeNow  = getTime()
        self.cnt = self.cnt + 1
        now      = timeNow-self.start
        if ( now - self.lastTime ) > self.printWait or ( self.cnt == self.max and self.max >= 3):
            self.lastTime = now - ( now % self.printWait )
            countPar      = self.cnt/self.max
            cmp           = (timeNow-self.start)*(self.max/self.cnt)
            eta           = cmp - now
            timeNOW       = "経過："     + re.sub("\..*$","",str(pd.Timedelta(now)))
            timeCMP       = "完了見込：" + re.sub("\..*$","",str(pd.Timedelta(cmp)))
            timeETA       = "残余："     + re.sub("\..*$","",str(pd.Timedelta(eta)))
            printCnt = self.cnt
            printMax = self.max
            if printCnt > 99999999:
                printCnt = "over"
            if printMax > 99999999:
                printMax = "over"
                
            self.displayHandle.update("{:>8}/{:<8}  {:>7.2%} {}  {}  {}".format(printCnt,printMax,countPar,timeETA,timeNOW,timeCMP))
            
        if self.cnt == self.max:
            self.leaveStep()
        else:
            self.checkUnder()

# スタンプ集計型、実行時間計測処理
class timeStack:
    lastStamp  = None # 最終スタンプ
    stampDict  = {} # 集計先
    labelStack = [] # 浅い階層で呼び出された場合、より深い階層のラベルは全て破棄する
    
    # 呼び出された時点でのラベルを収集し、stampに積み上げる
    # メンバ変数にラベルの深度を持つ
    def __init__(self,_label=None):
        if _label is None:
            label = sys._getframe().f_back.f_code.co_name
        else:
            label = _label
        timeStack.labelStack.append(label)
        self.deep  = len(timeStack.labelStack)
        if timeStack.lastStamp is not None:
            self.oldLabel = timeStack.lastStamp[0]
        else:
            self.oldLabel = None
            
        self.call("start")
    def call(self,_subLabel = ""):
        if self.deep < len(timeStack.labelStack):
            timeStack.labelStack = timeStack.labelStack[:self.deep]
        timeStack.stamp(".".join(timeStack.labelStack+[_subLabel]))
        
    def __del__(self):
        self.call("end")
        timeStack.labelStack = timeStack.labelStack[:self.deep-1]
        if self.oldLabel is not None:
            timeStack.stamp(self.oldLabel)
        
    def stamp(_label):
        nowTime = getTime()
        if timeStack.lastStamp is not None:
            lastTime  = timeStack.lastStamp[1]
            lastLabel = timeStack.lastStamp[0]
            if timeStack.stampDict.get(lastLabel) is None:
                timeStack.stampDict[lastLabel] = 0
            timeStack.stampDict[lastLabel] += nowTime - lastTime
        timeStack.lastStamp = [_label,nowTime]
        
    def clear():
        timeStack.lastStamp  = None
        timeStack.stampDict  = {}
        timeStack.labelStack = []
    # Stackの情報を収集しラベル事の処理時間を集計
    def collect():
        
        totalTime = 0
        for value in timeStack.stampDict.values():
            totalTime += value
        if totalTime == 0:
            print("no time")
        else:
            print("total time {:>10.3} sec".format(totalTime*0.000000001))
            
            maxLabelSize = 0
            for key in timeStack.stampDict.keys():
                if len(key) > maxLabelSize:
                    maxLabelSize = len(key)
            outformat = "{:<"+str(maxLabelSize)+"} : {:7.2%} {:>10.3} sec"
            for key,value in timeStack.stampDict.items():
                print(outformat.format(key,value/totalTime,value*0.000000001))
        
        timeStack.clear()

# # スタンプ蓄積型、実行時間計測処理
# class timeStack:
#     stampStack = [] # ため続ける
#     labelStack = [] # 浅い階層で呼び出された場合、より深い階層のラベルは全て破棄する
    
#     # 呼び出された時点でのラベルを収集し、stampに積み上げる
#     # メンバ変数にラベルの深度を持つ
#     def __init__(self,_label=None):
#         if _label is None:
#             label = sys._getframe().f_back.f_code.co_name
#         else:
#             label = _label
#         timeStack.labelStack.append(label)
#         self.deep  = len(timeStack.labelStack)
#         if len(timeStack.stampStack) > 0:
#             self.oldLabel = timeStack.stampStack[-1][0]
#         else:
#             self.oldLabel = None
            
#         self.call("start")
#     def call(self,_subLabel = ""):
#         if self.deep < len(timeStack.labelStack):
#             timeStack.labelStack = timeStack.labelStack[:self.deep]
#         timeStack.stamp(".".join(timeStack.labelStack+[_subLabel]))
        
#     def __del__(self):
#         self.call("end")
#         timeStack.labelStack = timeStack.labelStack[:self.deep-1]
#         if self.oldLabel is not None:
#             timeStack.stamp(self.oldLabel)
        
#     def stamp(_label):
#         timeStack.stampStack.append([_label,getTime()])
        
#     def clear():
#         timeStack.stampStack = []
#         timeStack.labelStack = []
#     # Stackの情報を収集しラベル事の処理時間を集計
#     def collect():
        
#         if len(timeStack.stampStack) == 0:
#             return
#         totalTime = timeStack.stampStack[-1][1] - timeStack.stampStack[0][1]
#         if totalTime == 0:
#             print("no time")
#         else:
#             for i in range(1,len(timeStack.stampStack))[::-1]:
#                 timeStack.stampStack[i][1] -= timeStack.stampStack[i-1][1]
#             for i in range(len(timeStack.stampStack)-1):
#                 timeStack.stampStack[i][1] = timeStack.stampStack[i+1][1]
#             timeStack.stampStack[-1][1] = 0
            
#             outDict = {}
#             for i in range(len(timeStack.stampStack)):
#                 timestamp = timeStack.stampStack[i]
#                 name      = timestamp[0]
#                 if outDict.get(name) is None:
#                     outDict[name] = 0
#                 outDict[name] += timestamp[1]

#             print("total time {:>10.3} sec".format(totalTime*0.000000001))
#             for key in outDict.keys():
#                 print("{:<25} : {:7.2%} {:>10.3} sec".format(key,outDict[key]/totalTime,outDict[key]*0.000000001))
        
#         timeStack.clear()

