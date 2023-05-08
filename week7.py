from asyncio.windows_events import NULL
import os
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import folium
import webbrowser
from folium.plugins import HeatMap
import pandas as pd

class DataAnalysis:
    '''
    数据分析类
    '''
    def __init__(self):
        self.files=[]
        self.stations=[]
    def load(self,folder_path):
        '''
        文件载入函数
        传入目录地址
        '''
        #读取目录下的所有文件名
        self.file_names=os.listdir(folder_path)
        #记录站点名称
        for file_name in self.file_names:
            self.stations.append(file_name.split('_')[2])
        #读取文件
        for file in self.file_names:
            f=pd.read_csv(folder_path+'/'+file,encoding='utf8')
            self.files.append(f)
        print("files have been loaded.")
    def fill_na(self,value=0):
        '''
        填补空值
        '''
        for i in tqdm(range(len(self.files)),desc='filling the NA value...'):
            self.files[i].fillna(value,inplace=True)
    def _test(self,pollutant):
        '''
        检验空值
        '''
        for df in self.files:
            for index,row in df.iterrows():
                if pd.isna(row['year']) or pd.isna(row['month']) or pd.isna(row['day']) or pd.isna(row['hour']):
                    raise NotNumError('time',row['No'],row['station'],row['year'],row['month'],row['day'],row['hour'],row[pollutant])
                elif pd.isna(row[pollutant]):
                    raise NotNumError('pollutant',row['No'],row['station'],row['year'],row['month'],row['day'],row['hour'],row[pollutant])
    def time_distribution(self,station,attribute,time_span=1):
        '''
        时间分布函数
        传入区域名,待查找的属性,时间间隔(默认时间点)
        返回分布字典{时间:含量}
        '''
        self._test(attribute)
        times={}
        #选择匹配的station文件
        for i in range(len(self.file_names)):
            if station==self.stations[i]:
                file=self.files[i]
                break
        #生成分布字典
        for index,row in tqdm(file.iterrows(),desc='calculating time distribution...'):
            if index%time_span==0:
                time=str(row['year'])+'/'+str(row['month'])+'/'+str(row['day'])+'/'+str(row['hour'])
                times.update({time:row[attribute]})
            else:
                times[time]+=row[attribute]
        return times
    def space_distribution(self,time,attribute,time_span=1):
        '''
        空间分布函数
        传入时间,待查找的属性,时间间隔(默认时间点)
        返回字典{地点:含量}
        '''
        self._test(attribute)
        year,month,day,hour=time.split('/')
        year=int(year)
        month=int(month)
        day=int(day)
        hour=int(hour)
        spaces={}
        for i in tqdm(range(len(self.files)),desc='calculating space distribution...'):
            flag=0
            for index,row in self.files[i].iterrows():
                if row['year']==year and row['month']==month and row['day']==day and row['hour']==hour:
                    if row[attribute]==NULL:
                        spaces.update({self.stations[i]:0})
                    else:
                        spaces.update({self.stations[i]:row[attribute]})
                    flag=1
                elif flag>0 and flag<time_span:
                    flag+=1
                    spaces[self.stations[i]]+=row[attribute]
                elif flag>=time_span:
                    break
        return spaces

class DataVisualization:
    '''
    分析结果可视化类
    '''
    def __init__(self,data:dict,attribute:str):
        self.attribute=attribute
        self.data=data
    def show_plot(self):
        '''
        绘制折线图
        '''
        x=self.data.keys()
        y=self.data.values()
        ax = plt.axes()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(len(x)/4))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(len(x)/48))
        plt.plot(x,y)
        plt.show()
    def show_pie(self):
        '''
        绘制饼状图
        '''
        x=self.data.values()
        labels=self.data.keys()
        plt.pie(x,labels=labels,autopct='%1.2f%%')
        plt.show()
    def show_map(self):
        '''
        绘制地图
        '''
        location={'Aotizhongxin':[116.40,39.99],'Changping':[116.23,40.22],'Dingling':[116.23,40.29],
                  'Dongsi':[116.42,39.92],'Guanyuan':[116.36,39.94],'Gucheng':[116.18,39.91],
                  'Huairou':[116.58,40.33],'Nongzhanguan':[116.47,39.94],'Shunyi':[116.67,40.16],
                  'Tiantan':[116.41,39.88],'Wanliu':[116.30,39.97],'Wanshouxigong':[116.37,39.88]}
        stations=list(self.data.keys())
        loc=[]
        for station in stations:
            loc.append(location[station])
        values=list(self.data.values())
        data=[[loc[i][1],loc[i][0],values[i]] for i in range(len(location))]
        center0=0
        center1=0
        center=[39.9075000,116.3880556]#设天安门为中心
        m=folium.Map(location=center,zoom_start=10)
        HeatMap(data,radius=15).add_to(m)
        m.save(self.attribute+'.html')
        webbrowser.open(self.attribute+'.html',new=2)
        
class NotNumError(ValueError):
    def __init__(self,type,No,station,year,month,day,hour,pollutant):
        if type=='time':#时间缺失
            self.message='time in row {} is missing!station: {} pollutant: {}'.format(No,station,pollutant)
        elif type=='pollutant':#含量缺失
            self.message='pollutant in row {} is missing!{}: {}/{}/{}/{}'.format(No,station,year,month,day,hour)
def main():
    folder_path='D:/Project/Python/week7Analysis/PRSA_Data_20130301-20170228'
    attribute='PM2.5'
    time='2015/6/25/15'
    data=DataAnalysis()
    data.load(folder_path)
    #data.fill_na()
    try:
        sd=data.space_distribution(time,attribute)
    except NotNumError as nne:
        print(nne.message)
if __name__=='__main__':main()