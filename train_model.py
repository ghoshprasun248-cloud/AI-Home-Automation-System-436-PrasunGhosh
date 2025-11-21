from app.ai import SchedulerAI, save_model
import pandas as pd

def generate_data(devs, days=60):
    rows=[]
    for day in range(days):
        for hour in range(24):
            for d in devs:
                weekday=day%7
                is_home=1 if hour in range(6,22) else 0
                t=0
                if d=='light_living' and hour>=18: t=1
                if d=='plug_coffee' and hour==7: t=1
                if d=='thermostat' and hour in (6,7,18,19): t=1
                rows.append({'device_id':d,'hour':hour,'weekday':weekday,'is_home':is_home,'target_on':t})
    return pd.DataFrame(rows)

if __name__=='__main__':
    devs=['light_living','plug_coffee','thermostat']
    df=generate_data(devs)
    ai=SchedulerAI()
    score=ai.train_df(df)
    print('score=',score)
    save_model(ai)
    print('saved model')
