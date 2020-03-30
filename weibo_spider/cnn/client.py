from io import BytesIO
import numpy as np
from PIL import Image
from keras import backend as K

from .model import net
from .utils import resize_image


class Caller:
    weights_path = 'cnn/model_data/weights.h5'
    in_shape = (40, 100, 3)

    number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    classes = number + alphabet
    n_classes = len(classes)
    char_len = 5

    def __init__(self):
        K.clear_session()  # load_weights()前需要clear_session()，原因未知
        self.model = net(in_shape=self.in_shape, n_classes=self.n_classes, char_len=self.char_len)
        self.model.load_weights(self.weights_path, by_name=True, skip_mismatch=True)

    def run(self, content):
        byte_stream = BytesIO(content)
        image = Image.open(byte_stream)
        image = resize_image(image, self.in_shape)
        input_data = np.array([image])
        sess = K.get_session()  # 注意不要sess.close()，否则再次get_session()会提示session已关闭
        out = sess.run(self.model.output, feed_dict={self.model.input: input_data})
        result = ''.join([self.classes[int(np.argmax(i[0]))] for i in out])
        return result
