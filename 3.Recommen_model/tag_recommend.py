# 패키지 호출
import os
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
import re
# from google.colab import drive
# drive.mount('/content/drive')

## 태그 전처리(지역정보제거)
def location(cat):
  for i in range(len(cat)):
    try:
      cat['keyword'][i] = str(cat['keyword'][i]).replace('대전','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('서울','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('대구','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('울산','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('부산','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('경기도','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('수지','')
      cat['keyword'][i] = str(cat['keyword'][i]).replace('NaN','')
    except: pass
  return(cat)

## 데이터 merge
def merge_df(df):
    df.fillna(0,inplace=True)
    df.replace(0,'',inplace=True)
    df['merge'] = df['title'] + ' '+df['cat1'] #+ df['cat2'] + df['cat3']
    df = df[['merge','keyword']]
    df.rename(columns={'merge':'feature', 'keyword' : 'label'}, inplace=True)
    return df

## 정규표현식 전처리(카테고리별 따로 지정)
def proccessing(df):
  for i in range(len(df)):
    ## 노트북 한정
    if '인치' in df.feature[i]:
      df.feature[i] = re.sub('\W+',' ', df.feature[i].lower())
    else : 
      df.feature[i] = re.sub('\W+',' ', df.feature[i].lower())
      df.feature[i] = re.sub('[0-9]',' ', df.feature[i].lower())

  # 한글자 처리(상황따라 변동)
  for info in range(len(df)):
    title = df.feature[info].split(' ')
    temp =''
    for i in title: 
      if len(i) > 1:
        temp = temp + i + ' '
    df.feature[info] = temp
  return(df)


## 태그만 모아두는 리스트 생성 및 10번이상 노출된 태그 list 추출
def tag(cat):
  test = list(cat['label'])
  label_unique=''
  for i in range(len(test)):
    try : 
      label_unique += test[i]
    except : 
      pass
  label_unique = label_unique.split(',')
  label_unique = [v for v in label_unique if v]
  
  df = pd.DataFrame({'label_unique':label_unique, 'count':0}).groupby(['label_unique']).count().reset_index()
  df = df[df['count']>10].sort_values(by='count',ascending=False).reset_index()[['label_unique','count']]
  top = list(df['label_unique'])

  return(top)

## 태그 분배 함수
def split_label(cat):
  for i in range(1,6):
    cat[f'label{i}'] = cat.label.str.split(',').str[i]
  cat = cat.fillna(0)
  return(cat)  


## 문서 유사도 계산 함수
def tfidf(proccessed_cat):
  from sklearn.feature_extraction.text import CountVectorizer
  vect = CountVectorizer()
  countvect = vect.fit_transform(proccessed_cat)

  countvect_df = pd.DataFrame(countvect.toarray(), columns = sorted(vect.vocabulary_))

  from sklearn.feature_extraction.text import TfidfVectorizer
  vect = TfidfVectorizer(max_features = 10000)
  tfvect = vect.fit(proccessed_cat)

  tfidv_df = pd.DataFrame(tfvect.transform(proccessed_cat).toarray(), columns = sorted(vect.vocabulary_))
  return(tfidv_df)

## 태그별 문서 유사도 계산
def make_matrix(tag_,cat):
  total_lab = pd.DataFrame()
  for label in tqdm(tag_):
    temp = pd.DataFrame()
    for i in range(len(cat)):
        if cat['label1'][i] == label:
            temp = pd.concat([temp, cat.iloc[[i]]])
        elif cat['label2'][i] == label:
            temp = pd.concat([temp, cat.iloc[[i]]])
        elif cat['label3'][i] == label:
            temp = pd.concat([temp, cat.iloc[[i]]])
        elif cat['label4'][i] == label:
            temp = pd.concat([temp, cat.iloc[[i]]])
        elif cat['label5'][i] == label:
            temp = pd.concat([temp, cat.iloc[[i]]])
    try:
      temp_tfidf = tfidf(temp['feature'])
      temp_tfidf['label'] = label
      temp_tfidf = temp_tfidf.groupby('label').mean().reset_index()
      total_lab = pd.concat([total_lab,temp_tfidf])
    except: pass
  total_lab = total_lab.fillna(0)

  return(total_lab)

## 입력한 제목 전처리 및 태그출력
# title = [input('제목을 입력해주세요 : ')]
def find_tag(title, cat_matrix):
  # test = proccessed_input(list(title))
  test = title[0].split(' ')
  for i, j in enumerate(test):
    i = re.sub('\W+',' ', j)
  test_input = []
  for i in test:
    if i in cat_matrix.columns:
      test_input.append(i)
  test_input.append('label')
  # 해당 카테고리에 적용
  test_matrix = cat_matrix[test_input]
  test_matrix
  # 상위 top5 태그 추출
  test_matrix['target'] = 0
  for i in range(len(test_input)-1):
    test_matrix['target'] += test_matrix[test_input[i]] 
  test_matrix['target'] = test_matrix['target'] / (len(test_input)-1)
  test_matrix = test_matrix[['label','target']].sort_values(by='target', ascending=False)[:5]
  return(test_matrix)

# # 특수문자
# def proccessing(df):
# ## 2글자 중 필요없는 리스트만 따로 생성
#   cat_list = (df.cumsum().iloc[-1].feature)
#   cat_list = cat_list.split(' ')
#   cat_list = [v for v in cat_list if v]

#   temp = []
#   for i in cat_list:
#     if (i not in temp) and (len(i) > 2):# or (len(i) == 3) or (len(i) == 4) or (len(i) == 5)):
#       temp.append(i)

#   train=[]
#   for i in temp:
#     if (i != 'i3') or (i != 'i5') or (i != 'i7') or (i != 'i9'):
#       i = re.sub('[^a-z0-9]+','', i)
#       train.append(i)
#   train = [v for v in train if v]
#   train.append('ㅜㅜ')

#   for i in range(len(df)):
#     ## 노트북 한정
#     if '인치' in df.feature[i]:
#       df.feature[i] = re.sub('\W+',' ', df.feature[i].lower())
#     # ## 특수문자
#     else : 
#       df.feature[i] = re.sub('\W+',' ', df.feature[i].lower())
#       df.feature[i] = re.sub('r[0-9]',' ', df.feature[i].lower())


#   for info in range(len(df)):
#     title = df.feature[info].split(' ')
#     temp =''
#     for i in title: 
#       if (len(i) > 1) and (i not in train):
#         temp = temp + i + ' '
#     df.feature[info] = temp
#   return(df)