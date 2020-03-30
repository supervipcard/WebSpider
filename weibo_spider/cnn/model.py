"""
定长字母数字验证码训练模型
"""
from functools import reduce

from keras.layers import Input, Conv2D, Dense, MaxPool2D, Flatten, Dropout
from keras.layers.advanced_activations import LeakyReLU, ReLU
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.models import Model


def compose(*funcs):
    if funcs:
        return reduce(lambda f, g: lambda *a, **kw: g(f(*a, **kw)), funcs)
    else:
        raise ValueError('Composition of empty sequence not supported.')


def Conv2D_BN_Leaky(*args, **kwargs):
    conv_kwargs = {'use_bias': False, 'kernel_regularizer': l2(5e-3), 'padding': 'same'}
    conv_kwargs.update(kwargs)
    return compose(
        Conv2D(*args, **conv_kwargs),
        BatchNormalization(),
        LeakyReLU(alpha=0.1))


def net(in_shape=(40, 100, 3), n_classes=36, char_len=4):
    in_layer = Input(in_shape)
    x = Conv2D_BN_Leaky(32, (3, 3))(in_layer)
    x = Conv2D_BN_Leaky(32, (3, 3))(x)
    x = MaxPool2D(2, 2, padding='same')(x)
    x = Dropout(rate=0.3)(x)
    x = Conv2D_BN_Leaky(64, (3, 3))(x)
    x = Conv2D_BN_Leaky(64, (3, 3))(x)
    x = MaxPool2D(2, 2, padding='same')(x)
    x = Dropout(rate=0.3)(x)
    x = Conv2D_BN_Leaky(128, (3, 3))(x)
    x = Conv2D_BN_Leaky(128, (3, 3))(x)
    x = Conv2D_BN_Leaky(128, (3, 3))(x)
    x = MaxPool2D(2, 2, padding='same')(x)
    x = Dropout(rate=0.3)(x)
    x = Conv2D_BN_Leaky(256, (3, 3))(x)
    x = Conv2D_BN_Leaky(256, (3, 3))(x)
    x = Conv2D_BN_Leaky(256, (3, 3))(x)
    x = MaxPool2D(2, 2, padding='same')(x)
    x = Dropout(rate=0.3)(x)
    x = Flatten()(x)
    preds = [Dense(n_classes, activation='softmax')(x) for i in range(char_len)]
    model = Model(in_layer, preds)
    return model


if __name__ == '__main__':
    model = net()
    print(model.summary())
