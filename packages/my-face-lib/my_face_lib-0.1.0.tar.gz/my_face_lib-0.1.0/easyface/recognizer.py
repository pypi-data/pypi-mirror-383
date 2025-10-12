import numpy as np
from .detector import detect_faces
from .embedder import FaceEmbedder
import cv2

def compare_faces(img1_path, img2_path, model_path="models/arcface.onnx"):
    emb = FaceEmbedder(model_path)
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    box1 = detect_faces(img1_path)[0]
    box2 = detect_faces(img2_path)[0]

    face1 = img1[box1[1]:box1[3], box1[0]:box1[2]]
    face2 = img2[box2[1]:box2[3], box2[0]:box2[2]]

    emb1 = emb.get_embedding(face1)
    emb2 = emb.get_embedding(face2)

    similarity = np.dot(emb1, emb2)
    return similarity
