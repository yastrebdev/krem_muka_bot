# -*- coding: windows-1251 -*-
import re

import pandas as pd
import numpy as np

# for Box-Cox Transformation
from scipy import stats

# for min_max scaling
from mlxtend.preprocessing import minmax_scaling

# plotting modules
import seaborn as sns
import matplotlib.pyplot as plt

import datetime

from clear import (
    clear_empty_fields, drop_columns, rename_columns)

np.random.seed(0)

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
               'date']

rename_columns(df, new_columns)

df['is_completed'] =(
    df['is_completed'].apply(lambda x: True if x == 'да' else False))


def time_formatting(cell):
    try:
        time = str(cell).strip().lower()

        clear_time = re.findall(r'[^А-ЯЁа-яё]+', time)
        print(clear_time)

        if pd.isna(cell) or str(cell).strip() == '':
            time = '00:00'

        return pd.Series([time, ''])

    except Exception as e:
        print(f'time_formating error: {e}')
        return pd.Series(['00:00', ''])


df[['time', 'time_comment']] = df['time'].apply(lambda cell: pd.Series(time_formatting(cell)))

pd.set_option('display.max_rows', None)

# print(df[['time', 'time_comment']])