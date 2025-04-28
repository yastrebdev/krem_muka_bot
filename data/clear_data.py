# -*- coding: windows-1251 -*-

import pandas as pd
import numpy as np

from clear.clear_empty_fields import clear_empty_fields
from clear.drop_columns import drop_columns
from clear.rename_columns import rename_columns

orders_data = pd.read_csv("data/km_orders.csv", sep=";", encoding="Windows-1251", skiprows=1)

cd, pm = clear_empty_fields(orders_data, np)

df = pd.DataFrame(cd)
df = drop_columns(df, ['число', 'Начинка', 'ФИО', 'месяц'])

new_columns = ['is_completed',
               'delivery_method',
               'time',
               'product',
               'description',
               'source',
               'summ',
               'delivery_price',
               'flau_price',
               'prepayment',
               'event',
               'data']

rename_columns(df, new_columns)

df['is_completed'] =(
    df['is_completed'].apply(lambda x: True if x == 'да' else False))

def process_time(x):
    if pd.isna(x):
        return "00:00"

    return x

df['time'] = df['time'].apply(process_time)

print(df)