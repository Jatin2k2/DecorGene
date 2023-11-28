import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input
import keras.models
from keras.models import model_from_json

with open('model/model.json', 'r') as f:
    model_json = f.read()

MLmodel = model_from_json(model_json)
MLmodel.load_weights("model/interior_design_model.h5")

def predict(img_path):
    image = load_img(img_path, target_size=(224, 224))
    image_data = img_to_array(image)
    preprocessed_image_data = np.expand_dims(image_data, axis=0)
    preprocessed_image_data = preprocess_input(preprocessed_image_data)
    prediction = MLmodel.predict(preprocessed_image_data)
    class_label = np.argmax(prediction)
    return class_label