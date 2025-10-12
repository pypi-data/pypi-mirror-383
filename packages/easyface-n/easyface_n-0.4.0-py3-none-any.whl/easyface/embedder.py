import onnxruntime as ort
import cv2
import numpy as np
import os

class FaceEmbedder:
    def __init__(self, model_path=None):
        # Default possible model locations
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_arcface = os.path.join(base_dir, "models", "arcface.onnx")
        buffalo_model = os.path.join(base_dir, "models", "buffalo_l", "w600k_r50.onnx")

        # Auto-detect which model to use
        if model_path and os.path.exists(model_path):
            self.model_path = model_path
        elif os.path.exists(default_arcface):
            self.model_path = default_arcface
        elif os.path.exists(buffalo_model):
            self.model_path = buffalo_model
        else:
            raise FileNotFoundError(
                f"No model found. Expected one of:\n"
                f" - {default_arcface}\n"
                f" - {buffalo_model}"
            )

        print(f"[INFO] Loading model: {self.model_path}")
        self.session = ort.InferenceSession(self.model_path)

    def preprocess(self, face):
        face = cv2.resize(face, (112, 112))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = face.transpose(2, 0, 1).astype(np.float32) / 255.0
        face = np.expand_dims(face, axis=0)
        return face

    def get_embedding(self, face_img):
        inp = self.preprocess(face_img)
        embedding = self.session.run(None, {"input.1": inp})[0][0]
        return embedding / np.linalg.norm(embedding)
