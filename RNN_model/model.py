from tensorflow.keras import layers, Input, Sequential


def RNN_bilstm(datanum):

    model = Sequential()
    model.add(Input(shape=(datanum, 1)))
    model.add(layers.Bidirectional(layers.LSTM(units=1, return_sequences=True)))

    model.add(layers.Dropout(0.3))

    model.add(layers.Bidirectional(layers.LSTM(units=1, return_sequences=False)))
    model.add(layers.Dropout(0.2))

    model.add(layers.Dense(units=datanum, activation="relu"))
    model.add(layers.Dense(datanum))
    model.summary()

    return model
