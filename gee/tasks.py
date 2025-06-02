from celery import shared_task
from django.utils import timezone
from image.models.image_model import ImageModel
# To avoid circular import if EarthEngineService itself imports tasks directly or indirectly,
# it's sometimes safer to instantiate it within the task or ensure no top-level imports create loops.
# from .services.earth_engine_service import EarthEngineService
# For now, assuming direct import is fine based on typical Celery structure.
# If circular dependency error occurs, will need to adjust.

@shared_task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=5*60) # Updated decorator
def process_gee_image_task(self, image_record_id: int): # Signature already correct for bind=True
    """
    Celery task to process a GEE image asynchronously.
    Calculates spectral indices and updates the ImageModel.
    """
    # Import service here to avoid potential Django app loading issues with Celery workers
    # and to manage dependencies more locally if needed.
    from gee.services.earth_engine_service import EarthEngineService

    try:
        image_record = ImageModel.objects.get(id=image_record_id)
    except ImageModel.DoesNotExist:
        print(f"Error: ImageModel with id {image_record_id} not found in process_gee_image_task.")
        # No need for self.update_state for DoesNotExist, as this is not a retryable GEE error.
        return f"Image record {image_record_id} not found. Task aborted."

    # Check if the task should run, e.g. if it was manually re-queued despite being COMPLETED
    # or if it's already PROCESSING by another worker (though Celery deduplication might handle some of this)
    if image_record.processing_status == ImageModel.ProcessingStatus.COMPLETED and not self.request.called_directly:
        print(f"Image {image_record_id} is already COMPLETED. Skipping task unless called directly.")
        return f"Image {image_record_id} already processed."

    # Mark as PROCESSING
    image_record.processing_status = ImageModel.ProcessingStatus.PROCESSING
    image_record.processing_error = None # Clear previous errors
    image_record.save(update_fields=['processing_status', 'processing_error'])
    print(f"Task started: Processing image {image_record_id} ({image_record.gee_asset_id})")

    try:
        service = EarthEngineService() # Initialize GEE service
        indices_data = service.calculate_spectral_indices(image_record.gee_asset_id)

        if indices_data and not isinstance(indices_data, dict): # Ensure it's a dict, not an error indicator
            # This check might be redundant if calculate_spectral_indices always returns a dict or throws error
            print(f"Warning: indices_data for image {image_record_id} might not be a dictionary. Type: {type(indices_data)}")

        if indices_data and \
           indices_data.get('ndvi_data') and \
           indices_data.get('ndwi_data') and \
           indices_data.get('ndti_data'):

            image_record.ndvi_data = indices_data.get('ndvi_data')
            image_record.ndwi_data = indices_data.get('ndwi_data')
            image_record.ndti_data = indices_data.get('ndti_data')

            image_record.ndvi_mean = indices_data.get('ndvi_data', {}).get('mean')
            image_record.ndwi_mean = indices_data.get('ndwi_data', {}).get('mean')
            image_record.ndti_mean = indices_data.get('ndti_data', {}).get('mean')

            image_record.processing_status = ImageModel.ProcessingStatus.COMPLETED
            image_record.processed_at = timezone.now()
            image_record.processing_error = None
            print(f"Successfully processed image {image_record_id}. Status: COMPLETED.")
        else:
            image_record.processing_status = ImageModel.ProcessingStatus.ERROR
            error_message = "Erreur calcul indices spectraux durant tâche asynchrone."
            if isinstance(indices_data, dict) and indices_data.get('error'):
                 error_message = indices_data.get('error')
            elif not indices_data:
                 error_message = "No data returned from calculate_spectral_indices."

            image_record.processing_error = error_message
            print(f"Error processing image {image_record_id}. Status: ERROR. Reason: {error_message}")

        image_record.save()
        return f"Image {image_record_id} processing finished with status: {image_record.processing_status}"

    except Exception as e:
        print(f"Exception in process_gee_image_task for image {image_record_id}: {e}")
        # This block is reached if an exception occurs in the main try block above.
        # The autoretry_for mechanism will handle retries for 'Exception' types.
        # Log the error and update the model state to ERROR.
        # If this is the last retry, the task will be marked as FAILED by Celery.
        error_message_for_db = f"Tâche asynchrone échouée après {self.request.retries + 1} tentatives: {type(e).__name__} - {str(e)}"
        print(f"Exception in process_gee_image_task for image {image_record_id} (attempt {self.request.retries + 1}/{self.max_retries}): {e}")

        try:
            # Re-fetch to ensure we have the latest version before updating, though image_record should be fine.
            image_record_on_failure = ImageModel.objects.get(id=image_record_id)
            image_record_on_failure.processing_status = ImageModel.ProcessingStatus.ERROR
            image_record_on_failure.processing_error = error_message_for_db
            image_record_on_failure.save(update_fields=['processing_status', 'processing_error'])
        except ImageModel.DoesNotExist:
            # This shouldn't happen if we found it at the start of the task.
            print(f"CRITICAL: ImageModel {image_record_id} not found when trying to save error state.")
        except Exception as e_save:
            print(f"CRITICAL: Failed to save error status for image {image_record_id} after task failure: {e_save}")

        # Re-raise the exception. This is crucial for autoretry_for to work.
        # Celery will catch this and schedule a retry if conditions are met.
        raise e
