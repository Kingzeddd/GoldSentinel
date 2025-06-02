from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone # Not strictly needed here yet, but good for Django commands
from image.models.image_model import ImageModel
from gee.services.earth_engine_service import EarthEngineService

class Command(BaseCommand):
    help = 'Scans for recent GEE images for the configured region and queues them for processing if not already processed.'

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--months_back',
    #         type=int,
    #         default=3, # Default to 3 months as in EarthEngineService
    #         help='Number of months back to scan for recent GEE images.'
    #     )
    #     # Add other arguments as needed, e.g., cloud_cover_max

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("Starting scan for recent GEE images..."))

        try:
            gee_service = EarthEngineService()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to initialize EarthEngineService: {e}"))
            return

        # months_back_arg = options.get('months_back')
        # For now, using the default in get_recent_images.
        # If arguments were added, they would be passed here:
        # recent_assets = gee_service.get_recent_images(months_back=months_back_arg)

        try:
            recent_assets = gee_service.get_recent_images() # Uses default months_back from the service
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to get recent images from GEE: {e}"))
            return

        if not recent_assets:
            self.stdout.write(self.style.NOTICE("No recent GEE image assets found."))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(recent_assets)} recent GEE assets. Checking against database..."))

        queued_count = 0
        skipped_completed_count = 0
        skipped_processing_count = 0
        requeued_error_count = 0

        for asset_info in recent_assets:
            gee_asset_id = asset_info.get('gee_asset_id')
            if not gee_asset_id:
                self.stdout.write(self.style.WARNING("Found an asset with no GEE ID. Skipping."))
                continue

            try:
                existing_image = ImageModel.objects.filter(gee_asset_id=gee_asset_id).first()

                if existing_image:
                    if existing_image.processing_status == ImageModel.ProcessingStatus.COMPLETED:
                        self.stdout.write(self.style.NOTICE(f"Image {gee_asset_id} already COMPLETED. Skipping."))
                        skipped_completed_count += 1
                        continue
                    elif existing_image.processing_status in [ImageModel.ProcessingStatus.PROCESSING, ImageModel.ProcessingStatus.PENDING]:
                        self.stdout.write(self.style.NOTICE(f"Image {gee_asset_id} already {existing_image.processing_status}. Skipping."))
                        skipped_processing_count += 1
                        continue
                    elif existing_image.processing_status == ImageModel.ProcessingStatus.ERROR:
                        self.stdout.write(self.style.WARNING(f"Image {gee_asset_id} previously ERRORED. Attempting to re-queue for processing..."))
                        # The process_image_complete method now handles re-queueing or creating new if needed
                        # It also checks if an image is already PENDING/PROCESSING for this asset_id
                        image_record = gee_service.process_image_complete(gee_asset_id=gee_asset_id, user_id=None) # user_id=None for system tasks
                        if image_record and image_record.processing_status == ImageModel.ProcessingStatus.PENDING:
                            self.stdout.write(self.style.SUCCESS(f"Successfully re-queued errored image {gee_asset_id} as new Image record ID {image_record.id}."))
                            requeued_error_count +=1
                        elif image_record: # if it was returned but not PENDING (e.g. already COMPLETED or still PROCESSING)
                             self.stdout.write(self.style.NOTICE(f"Re-queue attempt for errored image {gee_asset_id} resulted in status {image_record.processing_status}."))
                        else:
                            self.stderr.write(self.style.ERROR(f"Failed to re-queue errored image {gee_asset_id}."))
                        continue

                # If not existing_image or if we decided to create a new one for an errored one (handled by process_image_complete's logic)
                self.stdout.write(self.style.HTTP_INFO(f"Found new GEE asset: {gee_asset_id}. Attempting to queue for processing."))
                image_record = gee_service.process_image_complete(gee_asset_id=gee_asset_id, user_id=None)

                if image_record and image_record.processing_status == ImageModel.ProcessingStatus.PENDING:
                    self.stdout.write(self.style.SUCCESS(f"Successfully queued image {gee_asset_id} as Image record ID {image_record.id}."))
                    queued_count += 1
                elif image_record: # Image already existed and was handled (e.g. already processing)
                     self.stdout.write(self.style.NOTICE(f"Image {gee_asset_id} was already known with status {image_record.processing_status}."))
                     # This case might be covered by the checks above, but process_image_complete has its own logic
                else:
                    self.stderr.write(self.style.ERROR(f"Failed to queue image {gee_asset_id} for processing."))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"An error occurred while processing asset {gee_asset_id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Scan complete. "
            f"{queued_count} new images queued. "
            f"{requeued_error_count} errored images re-queued. "
            f"{skipped_completed_count} already completed. "
            f"{skipped_processing_count} already processing/pending."
        ))
