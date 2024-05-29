from transformers import pipeline

def load_huggingface_model():

    # Use a pipeline as a high-level helper
    pipe = pipeline("text-classification", model="valpy/prompt-classification")
    return pipe