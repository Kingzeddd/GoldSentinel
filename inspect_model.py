import os
import tensorflow as tf
from django.conf import settings
import django
from pathlib import Path # Ensure Path is imported

def main():
    print("Configuring Django settings...")
    try:
        # This environment should have DJANGO_SETTINGS_MODULE set.
        # If not, django.setup() might fail or use default settings.
        django.setup()
        print("Django setup complete.")
        base_dir_path = settings.BASE_DIR
        print(f"Using BASE_DIR from Django settings: {base_dir_path}")
    except Exception as e:
        print(f"Error during Django setup or accessing settings.BASE_DIR: {e}")
        print("Falling back to /app as base_dir_path.")
        base_dir_path = Path("/app") # Default to /app if settings are not loaded

    print(f"TensorFlow version: {tf.__version__}")

    model_name = 'ghana_mining_detector.h5'
    # Ensure base_dir_path is a string for os.path.join if it's a Path object
    model_path = os.path.join(str(base_dir_path), 'ai', 'models', model_name)

    print(f"Attempting to load model from: {model_path}")

    if not os.path.exists(model_path):
        print(f"Error: Model file does not exist at {model_path}")
        ai_models_dir = os.path.join(str(base_dir_path), 'ai', 'models')
        if os.path.exists(ai_models_dir):
            print(f"Contents of {ai_models_dir}: {os.listdir(ai_models_dir)}")
        else:
            print(f"Directory {ai_models_dir} does not exist.")
        return

    try:
        print("Loading Keras model...")
        # Suppress TensorFlow INFO/WARNING/ERROR messages related to GPU/CUDA for cleaner output
        # However, critical errors during model loading itself will still appear.
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # FATAL errors only
        tf.get_logger().setLevel('ERROR')

        model = tf.keras.models.load_model(model_path)
        print("Model loaded successfully.")

        print("\nModel Summary:")
        model.summary() # This prints to stdout, which is fine

        print("\nModel Input Shape:")
        if isinstance(model.input_shape, list):
             for i, shape in enumerate(model.input_shape):
                print(f"Input {i}: {shape}")
        else:
            print(model.input_shape)

        # For more detail on actual input layers (especially if named)
        print("\nInput Layer Details from model.inputs:")
        if model.inputs:
            for inp in model.inputs:
                 print(f"Name: {inp.name}, Shape: {inp.shape}, DType: {inp.dtype}")
        else:
            print("No inputs found via model.inputs attribute.")


    except Exception as e:
        print(f"An error occurred during model loading or inspection: {e}")

if __name__ == '__main__':
    # It's good practice to ensure DJANGO_SETTINGS_MODULE is set if running standalone.
    # The execution environment for `run_in_bash_session` should ideally handle this.
    # Example: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # django.setup() # Then call setup
    main()
