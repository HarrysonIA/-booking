from transformers import pipeline
def ethical_classifier():
    
    pipe = pipeline("text-classification", model="HarrysonIA/EthicalSentences")
    return pipe