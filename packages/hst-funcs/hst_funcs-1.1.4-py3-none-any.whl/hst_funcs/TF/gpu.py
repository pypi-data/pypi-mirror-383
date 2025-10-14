# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 07:40:26 2024
@author: S.T.Hwang
"""

# 입력 데이터가 너무 클 때, 잘게 짤라서 메모리에 올려주는 역할을 함
# DataGenerator로 메모리 업로드량 줄이기
#train_gen = DataGenerator(X_train, Y_train, 32)
#test_gen = DataGenerator(X_test, Y_test, 32)
from tensorflow.keras.utils import Sequence
class DataGenerator(Sequence):
    def __init__(self, x_set, y_set, batch_size):
        self.x, self.y = x_set, y_set
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
        return batch_x, batch_y