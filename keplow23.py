import zipfile
import os
import glob
from datetime import datetime

import pandas as pd
import numpy as np
from time import sleep

def scheck(series,count): #Series 인자로 받은 후 이상치값 분석, return 값보다 작으면 이상치
	if count==0:
		return 0	   
	anum=int(count/4)
	bnum=anum*3
	print(anum,' ',bnum)
	valuech=series[bnum]-series[anum]
	print(series)    
	value=series[anum]-(2*valuech)

	return value

def bcheck(series,count): #Series 인자로 받은 후 이상치값 분석, return 값보다 크면 이상치
	if count==0:
		return 0	   
	anum=int(count/4)
	bnum=anum*3
	valuech=series[bnum]-series[anum]
	value=series[bnum]+(2*valuech)

	return value	 	  

def printall(ertype,mid,day,num,tfile) :
	if ertype==1 :
		tfile.write(mid+'미터의 '+day+' 날짜의 데이터 갯수는 '+num+' 개 입니다.\n')
		tfile.write('갯수가 정상 범위가 아니므로 확인이 필요합니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	   
	elif ertype==2 :
		tfile.write(mid+' 의 '+day+' 날짜에 숫자가 아닌 데이터가 있습니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	
	elif ertype==3 :	
		tfile.write(mid+' 의 '+day+' 날짜의 데이터값이 이상합니다. 확인이 필요합니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	   

def glp(fname,tfile): #G,AE,S타입 LP검침
	data=pd.read_excel(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[["계기번호","검침시간","순방향유효전력","순방향지상무효전력","순방향진상무효전력","피상전력","역방향유효전력","역방향지상무효전력","역방향진상무효전력","역방향피상전력"]]
	data2.rename(columns={'순방향유효전력':'FEP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={'순방향지상무효전력':'LARAP'},inplace=True)
	data2.rename(columns={'순방향진상무효전력':'LERAP'},inplace=True)
	data2.rename(columns={'피상전력':'AP'},inplace=True)
	data2.rename(columns={'역방향유효전력':'APA'},inplace=True)	   
	data2.rename(columns={'역방향지상무효전력':'APB'},inplace=True)
	data2.rename(columns={'역방향진상무효전력':'APC'},inplace=True)	   
	data2.rename(columns={'역방향피상전력':'APD'},inplace=True)
	data2.rename(columns={'계기번호':'MeterID'},inplace=True)
	data2.rename(columns={'검침시간':'CTime'},inplace=True)
	data2['FEP']=pd.to_numeric(data2['FEP'],errors='coerce')
	data2['MeterID']=data2['MeterID'].astype(str)   
	print('location5\n')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	prov=100/data6.MeterID.count()

	for i in range(0,data6.MeterID.count()):
		data8=data2[(data2.MeterID==data6.MeterID[i])]
		data8=data8.sort_values(by='FEP',ascending=True)
		data8=data8.reset_index(drop=True)
		o=data8.FEP.count()		
		svalue=scheck(data8.FEP.values,o)
		bvalue=bcheck(data8.FEP.values,o)
		print(svalue)		   
		print(bvalue)		   
		kk=bvalue-svalue #이거 왜만들어놨지?
		sleep(0.1) #제대로 작동안하는듯하다
		for j in range(0,data7.CTime.count()):   # 아래의 경우 2*o로 사용가능 
			data8=data2[(data2.MeterID==data6.MeterID[i])]
			data8=data8.sort_values(by='FEP',ascending=True)
			data8=data8.reset_index(drop=True)
			print(data7.CTime[j])
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]   
			data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 	 
			k=data8.FEP.count() # 하루치 LP갯수
			print(k)		 
			if data7.CTime[j]=='전체' :
				print('나는 전체')	 
			else :		  
				data8['FEP']=pd.to_numeric(data8['FEP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
				data8['LARAP']=pd.to_numeric(data8['LARAP'],errors='coerce')
				data8['LERAP']=pd.to_numeric(data8['LERAP'],errors='coerce')
				data8['AP']=pd.to_numeric(data8['AP'],errors='coerce')    
				data8['APA']=pd.to_numeric(data8['APA'],errors='coerce')
				data8['APB']=pd.to_numeric(data8['APB'],errors='coerce')		  
				data8['APC']=pd.to_numeric(data8['APC'],errors='coerce')		  
				data8['APD']=pd.to_numeric(data8['APD'],errors='coerce')		  

				if k<96 | k>98: #일일 LP 개수가 정상이 아닐경우 체크
					if k!=0:  
						printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
   	 		
				check=data8['FEP'].isnull().sum()+data8['LARAP'].isnull().sum()+data8['LERAP'].isnull().sum()+data8['AP'].isnull().sum()
				if check>0:
					printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)				
				else:			
					if kk==0 :
						data10=data8[data8['FEP']>1000000]
					else:		   
						data10=data8[data8['FEP']<svalue]
						data10=data10+data8[data8['FEP']>bvalue]
						data10=data10+data8[data8['FEP']>1000000] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['FEP']<0] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['LARAP']>1000000]
					data10=data10+data8[data8['LARAP']<0]		 
					data10=data10+data8[data8['LERAP']>1000000]
					data10=data10+data8[data8['LERAP']<0]
					data10=data10+data8[data8['AP']>1000000]
					data10=data10+data8[data8['AP']<0]		 
					data10=data10+data8[data8['APA']>1000000]
					data10=data10+data8[data8['APA']<0]	
					data10=data10+data8[data8['APB']>1000000]
					data10=data10+data8[data8['APB']<0]	
					data10=data10+data8[data8['APC']>1000000]
					data10=data10+data8[data8['APC']<0]	
					data10=data10+data8[data8['APD']>1000000]
					data10=data10+data8[data8['APD']<0]	

					if data10.empty==False: #하나라도 쓰레기값 범위인 경우
						printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)	 


list_of_files = sorted(glob.glob(os.getcwd()),key=os.path.getmtime) # octet-stream파일이 저장되는 경로를 지정
latest_file = max(list_of_files, key=os.path.getctime)
	 
fantasy_zip = zipfile.ZipFile(latest_file)
path =os.getcwd()+' LPdata '+str(datetime.today().year)+'-'+str(datetime.today().month)+'-'+str(datetime.today().day) # 결과가 저장될 폴더
fantasy_zip.extractall(path)
 
fantasy_zip.close()

file_list = os.listdir(path)
file_list=''.join(file_list)
file_list=path+'\\'+file_list
print(file_list+'\nlocation1\n')
os.remove(latest_file)	 # 작업한 프로그램 삭제

filename=path+'\\'+str(datetime.today().year)+'-'+str(datetime.today().month)+'-'+str(datetime.today().day)+'-'+'분석 결과.txt'
tfile = open(filename, mode='wt', encoding='utf-8')


#filenamea=filename # 테스트용 코드
#filenameb=path+'\\'+str(datetime.now().minute)+'.txt' #테스트용 코드

glp(file_list,tfile)

while True:
	#print('while문 진입\n\n')
	list_of_files = glob.glob(os.getcwd()) # octet-stream파일이 저장되는 경로를 지정
	
	latest_file = max(list_of_files, key=os.path.getctime)
	print(latest_file+'\n')
	print(latest_file[-12:]+'\nlocation2\n')
	if latest_file[-12:]!='octet-stream' :  #가장 최근파일의 확장자가 octet-stream이 아닌경우에 와일문 종료
		#print('잡았는데?\n')
		print('location3\n')
		break
	
	#print('통과했다\n')
	fantasy_zip = zipfile.ZipFile(latest_file)
	path = os.getcwd()+' LPdata '+str(datetime.today().year)+'-'+str(datetime.today().month)+'-'+str(datetime.today().day)
	fantasy_zip.extractall(path)
	print('location4\n')
	fantasy_zip.close()
	xlsfiles=glob.glob(path+'\\*')
	filename = max(xlsfiles, key=os.path.getctime)
	os.remove(latest_file)	 # 작업한 프로그램 삭제
	
	glp(filename,tfile)