import numpy as np

def compare_faces(embedding1, embedding2, threshold=0.5):
    sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return sim > threshold, sim
