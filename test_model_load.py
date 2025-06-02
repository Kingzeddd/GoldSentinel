import tensorflow as tf
model_path = "ai/models/ghana_model.h5"
try:
    model = tf.keras.models.load_model(model_path)
    print("Modèle chargé avec succès !")
except Exception as e:
    print(f"Erreur lors du chargement : {e}")