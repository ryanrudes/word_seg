import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
import threading
import os
import time
import requests
import random
import sys

from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.keras.datasets import *
from tensorflow.keras.applications import *
from tensorflow.keras.losses import *
from tensorflow.keras.experimental import *
from tensorflow.keras.optimizers import *
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

def download(i):
  global text
  r = requests.get("https://www.gutenberg.org/files/{}/{}-0.txt".format(i, i))
  if r.status_code == 200:
    text = text + str(r.content) + " "

text = ""
num_books, num_concurrent_threads = "10", "3"
num_books = int(num_books)
num_concurrent_threads = int(num_concurrent_threads)

for i in tqdm(range(0, num_books, num_concurrent_threads)):
  threads = []
  for j in range(i, i + num_concurrent_threads):
    threads.append(threading.Thread(target = download, args = (j,)))

  for thread in threads:
    thread.start()

  for thread in threads:
    thread.join()

print(len(text))

text = text[:-1].lower()

text = text.replace("\n", " ")

for character in np.setdiff1d(np.array(list(set(text))), np.array(list("abcdefghijklmnopqrstuvwxyz"))):
  text = text.replace(character, " ")

text = text.strip()

for i in tqdm(range(2, 100)):
  text = text.replace(" " * (101 - i), " ")

text_no_spaces = text.replace(" ", "")

vocab = list(set(text_no_spaces))

vocab_dict = {c:i for i, c in zip(np.arange(0, len(vocab)), vocab)}

text_no_spaces_one_hot = to_categorical([vocab_dict[character] for character in tqdm(text_no_spaces)], num_classes = 26)

indices = np.where(np.array(list(text)) == " ")[0]
indices = indices - np.arange(1, len(indices) + 1)

yes_no = np.zeros(len(text_no_spaces))
yes_no[indices] = 1

length = len(text_no_spaces_one_hot) - (len(text_no_spaces_one_hot) % 100)
text_no_spaces_one_hot = text_no_spaces_one_hot[:length]
yes_no = yes_no[:length]

X = text_no_spaces_one_hot.reshape((len(text_no_spaces_one_hot) // 100, 100, 26))

Y = yes_no.reshape((len(yes_no) // 100, 100))

point = int(np.floor(len(X) * 0.9))
X_train = X[:point]
Y_train = Y[:point]
X_test = X[point:]
Y_test = Y[point:]

print(X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)

"""
np.save("X_train.npy", X_train)
np.save("Y_train.npy", Y_train)
np.save("X_test.npy", X_test)
np.save("Y_test.npy", Y_test)
"""

batch_size = 256

model = Sequential()
model.add(Bidirectional(LSTM(500, stateful = True, return_sequences = True), batch_input_shape = (batch_size, 100, 26)))
model.add(Dense(1, activation = 'sigmoid'))
model.summary()

model.compile(optimizer = "adam", loss = "mean_squared_error", metrics = ["accuracy"])

losses = []
epochs = 100

for epoch in range(epochs):
  epoch_wise_losses = []

  random_idx = np.arange(0, len(X_train))
  np.random.shuffle(random_idx)
  x_train = X_train[random_idx]
  y_train = Y_train[random_idx]

  history = model.fit(x_train[:len(x_train) - (len(x_train) % batch_size)], y_train[:len(y_train) - (len(y_train) % batch_size)], batch_size = batch_size, verbose = 0)
  train_loss = np.mean(history.history["loss"])

  epoch_wise_losses.append(train_loss)
  print ("Epoch: {}/{}, Train Loss: {}".format(epoch, epochs, train_loss))

model.save("model.h5")
np.save("losses.npy", np.array(epoch_wise_losses))
