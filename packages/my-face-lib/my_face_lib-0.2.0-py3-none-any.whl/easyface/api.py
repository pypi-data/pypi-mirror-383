from .detector import FaceDetector
from .embedder import FaceEmbedder
from .compare import compare_faces
import cv2

detector = FaceDetector()
embedder = FaceEmbedder()

def load_image(path):
    return cv2.imread(path)

def encode_face(path):
    img = load_image(path)
    emb = embedder.get_embedding(img)
    return emb

def match(img1, img2):
    emb1 = encode_face(img1)
    emb2 = encode_face(img2)
    result, sim = compare_faces(emb1, emb2)
    return result, float(sim)
