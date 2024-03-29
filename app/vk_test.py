# -*- coding: utf-8 -*-
"""Задание_на_стажировку_№_2_ версия № 3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vHfuuExatXIM0CGAxf2Lq19Jyw2KrK6k
"""

# !unzip /content/drive-download-20240309T162137Z-001.zip

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#!pip install catboost
from catboost import CatBoostRanker, Pool
from copy import deepcopy
import os

from sklearn.metrics import ndcg_score

import warnings
warnings.filterwarnings("ignore")

# from google.colab import files
# uploaded = files.upload()

train_df = pd.read_csv('/home/app/train_df.csv')
test_df = pd.read_csv('/home/app/test_df.csv')

df_sum = train_df.groupby('search_id')['target'].sum().reset_index()
to_remove = set(df_sum[df_sum['target'] == 0]['search_id'].to_list())
print(len(to_remove))
train_non_zeros = train_df[~train_df['search_id'].isin(to_remove)]
train_non_zeros

train_non_zeros.groupby('search_id')['target'].sum()

train_df

train_df.groupby('target')['target'].count()

322 / 14759 + 322

test_df

train_df['search_id'].unique().__len__()

hist = train_df.groupby('search_id')['search_id'].count()
hist

plt.hist(hist, bins=20)

set(train_df['search_id'].unique()) & set(test_df['search_id'].unique())

"""Исходя из всего анализа выше:
Тут очень несбалансированный датасет, так как в среднем на группу приходиться по 1-2 примерам с положительным классом. Дисбаланс 322 к 1.

"""

X_train = train_df.drop(['search_id', 'target'] , axis=1).values
y_train = train_df['target'].values
group_id_train = train_df['search_id'].values

X_test = test_df.drop(['search_id', 'target' ], axis=1).values
y_test = test_df['target'].values
group_id_test = test_df['search_id'].values

"""### Катбуст хорошо работает с категориальными фичами, поэтому попробуем задетектить

Попробуем взять 19 и 34 первых как категориальные, так как там уникальных значений относительно немного
"""

feature2num_classes = {}
for col in train_df.drop(['search_id', 'target'], axis=1).columns:
    feature2num_classes[col] = len(train_df.groupby(col)[col])

features_values = list(sorted(feature2num_classes.items(), key=lambda x: x[1]))
print(features_values)

plt.plot([elem[1] for elem in features_values])

cat_features_19 = [int(elem[0].split('_')[1]) for elem in features_values[:19]]
cat_features_34 = [int(elem[0].split('_')[1]) for elem in features_values[:34]]

cat_features_19

X_train = train_non_zeros.drop(['search_id', 'target'] , axis=1).values
y_train = train_non_zeros['target'].values
group_id_train = train_non_zeros['search_id'].values

train_pool = Pool(
    data= X_train,
    label= y_train,
    group_id= group_id_train,
    # cat_features=cat_features_19
)

test_pool = Pool(
    data= X_test,
    label= y_test,
    group_id= group_id_test,
    # cat_features=cat_features_19
)

"""к сожалению, идея с категориальными признаками так же как и остальные способы буста не дала"""

from catboost import CatBoostClassifier, CatBoostRegressor, CatBoostRanker


parameters = {
    'iterations': 2000,
    'learning_rate': 1e-2,
    'depth': 6,
    # 'loss_function': 'YetiRankPairwise',
    # 'cat_features': cat_features_19,
    'class_weights': {
        0: 1,
        1: 10
    },

    'custom_metric': ['NDCG', 'PFound', 'PrecisionAt:top=5', 'RecallAt:top=5'],

    'verbose': False,
    'random_seed': 42,
}

model = CatBoostClassifier(**parameters)

model.fit(
    train_pool,
    eval_set=test_pool,
    silent=True,
    use_best_model=True
    #,plot=True
)

preds = model.predict(X_test)

print()
print(model.best_score_)

"""Итого видим: NDCG = 0.93 , recall =0.95 , но при этом Precision очень мал = 0.06
Причина- сильный дисбаланс, даже веса не помогли. Модель переобучается на 0.
"""
