import os
import numpy as np
from efficientnet_pytorch import EfficientNet
from PIL import Image
import torch
import torchvision.transforms as transforms
import io

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
# Load model
model_path = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "../models/plant_disease_i256_e1_b64_model.pth"))
try:
    model = EfficientNet.from_name('efficientnet-b0')
    model._fc = torch.nn.Linear(model._fc.in_features, 38)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper_bell___Bacterial_spot', 'Pepper_bell___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

nom_classe = [
    'Pomme - Tavelure du pommier',
    'Pomme - Pourriture noire',
    'Pomme - Rouille du cèdre et du pommier',
    'Pomme - Sain',
    'Myrtille - Sain',
    'Cerisier - Oïdium',
    'Cerisier - Sain',
    'Maïs - Tache foliaire à Cercospora (Gray leaf spot)',
    'Maïs - Rouille commune',
    'Maïs - Brûlure nordique des feuilles',
    'Maïs - Sain',
    'Vigne - Pourriture noire',
    'Vigne - Esca (Maladie des taches noires)',
    'Vigne - Brûlure des feuilles (Isariopsis)',
    'Vigne - Sain',
    'Orange - Huanglongbing (Greening des agrumes)',
    'Pêcher - Tache bactérienne',
    'Pêcher - Sain',
    'Poivron - Tache bactérienne',
    'Poivron - Sain',
    'Pomme de terre - Mildiou précoce',
    'Pomme de terre - Mildiou tardif',
    'Pomme de terre - Sain',
    'Framboise - Sain',
    'Soja - Sain',
    'Courge - Oïdium',
    'Fraisier - Brûlure des feuilles',
    'Fraisier - Sain',
    'Tomate - Tache bactérienne',
    'Tomate - Mildiou précoce',
    'Tomate - Mildiou tardif',
    'Tomate - Moisissure des feuilles',
    'Tomate - Tache septorienne',
    'Tomate - Acariens (Tétranyque à deux points)',
    'Tomate - Tache cible',
    'Tomate - Virus des feuilles jaunes en cuillère',
    'Tomate - Virus de la mosaïque',
    'Tomate - Sain'
]

# Preprocessing
def preprocess_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print(f"Image mode: {image.mode}, size: {image.size}")
        # Resize image to reduce memory usage
        image = image.resize((224, 224))
        print(f"Resized image size: {image.size}")
        # Manually convert to NumPy
        image_np = np.array(image, dtype=np.uint8)
        print(f"NumPy array shape: {image_np.shape}, dtype: {image_np.dtype}, type: {type(image_np)}")
        # Verify NumPy array type
        if not isinstance(image_np, np.ndarray):
            raise TypeError(f"Expected np.ndarray, got {type(image_np)}")
        # Use torch.tensor
        tensor = torch.tensor(image_np, dtype=torch.float32).permute(2, 0, 1) / 255.0
        print(f"Tensor shape: {tensor.shape}, dtype: {tensor.dtype}")
        transform = transforms.Compose([
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        tensor = transform(tensor)
        return tensor.unsqueeze(0).to(device)
    except Exception as e:
        print(f"Error in preprocess_image: {e}")
        raise