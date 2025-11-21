import os, pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

DEFAULT_MODEL_PATH='model/scheduler.pkl'

class SchedulerAI:
    def __init__(self):
        self.model=None
        self.enc=None

    def train_df(self, df):
        X=df[['device_id','hour','weekday','is_home']]
        self.enc=LabelEncoder().fit(X['device_id'])
        X['device_id']=self.enc.transform(X['device_id'])
        y=df['target_on']
        Xtr,Xte,Ytr,Yte=train_test_split(X,y,test_size=0.2)
        clf=RandomForestClassifier()
        clf.fit(Xtr,Ytr)
        self.model=clf
        return clf.score(Xte,Yte)

    def predict_now(self, device_id):
        if self.model is None: return None
        hour=int(pd.Timestamp.now().hour)
        weekday=int(pd.Timestamp.now().dayofweek)
        is_home=1
        try: d=self.enc.transform([device_id])[0]
        except: return None
        X=np.array([[d,hour,weekday,is_home]])
        return float(self.model.predict_proba(X)[0][1])

def save_model(ai):
    os.makedirs(os.path.dirname(DEFAULT_MODEL_PATH),exist_ok=True)
    with open(DEFAULT_MODEL_PATH,'wb') as f:
        pickle.dump({'model':ai.model,'enc':ai.enc},f)

def load_model(path=DEFAULT_MODEL_PATH):
    with open(path,'rb') as f:
        d=pickle.load(f)
    ai=SchedulerAI()
    ai.model=d['model']
    ai.enc=d['enc']
    return ai
