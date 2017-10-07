import csv
import pandas as pd

df = pd.read_csv("D:\\POO\\Py_work\\py_test.csv")

dic = {'isrm','card','finacial'}

for div in dic:
    df1 = df[['Division', 'Asv', 'AMI_days']]
    df2 = df1[df1.Division == div]
    df3 = df2[(df2['AMI_days'] > 90)]
    df4 = df3['Asv'].value_counts()
    #print div
    #print df4
    
    df3.to_csv("D:\\POO\\Py_work\\write_pandas.csv", mode = 'a')#, columns=["ASV","Counts"])

