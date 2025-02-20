from google.cloud import vision

class VisionService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def extract_text_from_image(self, image_content):
        image = vision.Image(content=image_content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        return ""

    def analyze_image(self, image_content):
        image = vision.Image(content=image_content)
        response = self.client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]
        return " ".join(labels)