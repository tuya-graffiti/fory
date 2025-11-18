import pandas as pd
from datas import filepaths as fp
import os
from conn import mysql_conn as mc

def insert_jpkb():
    JP_CSV = os.path.join(fp.FILES_DIR,'JP学科知识问答.csv')
    df = pd.read_csv(JP_CSV,encoding='utf-8')
    df.columns = ['subject_name','question','answer']
    ds = df.to_dict(orient='records')
    MC = mc.MysqlConn()
    MC.insert('jpkb',ds)
    MC.close()
if __name__ == '__main__':
    insert_jpkb()
