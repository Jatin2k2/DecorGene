import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input
import keras.models
from keras.models import model_from_json
styles = [
    "casual",
    "classic",
    "modern",
    "natural",
]

types = [
    "bathroom",
    "bedroom",
    "dining room",
    "kitchen",
    "living room"
]
# Append "model/" to paths
with open('model/typeModel.json', 'r') as f1:
    typeModel_JSON = f1.read()

with open('model/styleModel.json','r') as f2:
    styleModel_JSON = f2.read()

typeModel = model_from_json(typeModel_JSON)
typeModel.load_weights("model/typeModel.h5")
styleModel = model_from_json(styleModel_JSON)
styleModel.load_weights("model/styleModel.h5")

def predict(img_path):
    image = load_img(img_path, target_size=(224, 224))
    image_data = img_to_array(image)
    preprocessed_image_data = np.expand_dims(image_data, axis=0)
    preprocessed_image_data = preprocess_input(preprocessed_image_data)
    prediction_Type = typeModel.predict(preprocessed_image_data)
    prediction_Style = styleModel.predict(preprocessed_image_data)
    roomType = np.argmax(prediction_Type)
    roomStyle = np.argmax(prediction_Style)
    return types[roomType] + " " + styles[roomStyle]
