import onnxruntime as ort
import cv2
import numpy as np

class FaceEmbedder:
    def __init__(self, model_path="models/arcface.onnx"):
        self.session = ort.InferenceSession(model_path)

    def preprocess(self, face):
        face = cv2.resize(face, (112, 112))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = face.transpose(2, 0, 1).astype(np.float32) / 255.0
        face = np.expand_dims(face, axis=0)
        return face

    def get_embedding(self, face_img):
        inp = self.preprocess(face_img)
        embedding = self.session.run(None, {"data": inp})[0][0]
        return embedding / np.linalg.norm(embedding)
