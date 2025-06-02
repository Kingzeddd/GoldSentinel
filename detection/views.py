from django.http import JsonResponse
from detection.ai.ghana_detector import GhanaBasedDetector

def check_model_status(request):
    try:
        detector = GhanaBasedDetector()
        if detector.model is not None:
            return JsonResponse({
                "status": "success",
                "message": "Modèle Ghana chargé avec succès",
                "model_info": str(detector.model.summary())
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Le modèle Ghana n'est pas chargé"
            }, status=500)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors du chargement du modèle: {str(e)}"
        }, status=500)