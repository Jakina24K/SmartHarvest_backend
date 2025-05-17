from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import torch
from api.scripts.plant_process import preprocess_image, model, class_names
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def predict(request):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)
        
        img_bytes = request.FILES['file'].read()
        input_tensor = preprocess_image(img_bytes)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            pred_name = class_names[pred_class]
            pred_prob = probs[0][pred_class].item()

        response = {
            "class_index": pred_class,
            "class_name": pred_name,
            "probability": round(pred_prob, 4)
        }
        logger.info(f"Prediction response: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        return HttpResponseServerError(f"Error in predict: {e}")

@require_GET
def health(request):
    logger.info("Health check requested")
    return JsonResponse({"status": "ok"})