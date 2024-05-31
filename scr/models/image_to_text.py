from transformers import pipeline

def image_to_text():

    image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
    return image_to_text