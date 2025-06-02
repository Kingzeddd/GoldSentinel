from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile # For saving string content to FileField
# from django.conf import settings # Not strictly needed for this task's logic

from .models import ReportModel
from .services.report_service import ReportService

@shared_task(bind=True, autoretry_for=(Exception,), max_retries=3, default_retry_delay=2*60) # 2 minutes
def generate_report_task(self, report_id: int, user_id: int = None):
    """
    Celery task to generate a report asynchronously.
    `user_id` is passed for potential logging or if the service method needs it,
    though `ReportModel.generated_by` should already be set when the ReportModel instance is created.
    """
    try:
        report_instance = ReportModel.objects.get(id=report_id)
    except ReportModel.DoesNotExist:
        print(f"Error: ReportModel with id {report_id} not found in generate_report_task.")
        # No further action needed, task will not be retried for DoesNotExist if not part of autoretry_for.
        # If it were, self.update_state(...) could be used.
        return f"Report record {report_id} not found. Task aborted."

    # Avoid re-processing if already completed, unless called directly (e.g., for a retry or manual re-run)
    if report_instance.status == ReportModel.StatusChoices.COMPLETED and not self.request.called_directly:
        print(f"Report {report_id} is already COMPLETED. Skipping regeneration.")
        return f"Report {report_id} already generated and completed."

    report_instance.status = ReportModel.StatusChoices.PROCESSING
    report_instance.processing_error_message = None # Clear previous errors
    report_instance.save(update_fields=['status', 'processing_error_message'])
    print(f"Task started: Generating report for Report ID {report_id} (Type: {report_instance.report_type})")

    service = ReportService()
    report_data = None
    error_occurred = False
    error_message_str = "" # Changed variable name to avoid conflict with field name

    try:
        if report_instance.report_type == ReportModel.ReportTypeChoices.SUMMARY:
            report_data = service.generate_summary_report(
                start_date_str=report_instance.start_date.isoformat() if report_instance.start_date else None,
                end_date_str=report_instance.end_date.isoformat() if report_instance.end_date else None,
            )
        elif report_instance.report_type == ReportModel.ReportTypeChoices.ALERT_SUMMARY:
            report_data = service.generate_alert_summary_report(
                region_id=report_instance.region_id, # Pass region_id if it's stored on the model
                start_date_str=report_instance.start_date.isoformat() if report_instance.start_date else None,
                end_date_str=report_instance.end_date.isoformat() if report_instance.end_date else None,
            )
        # Add elif blocks for other report types from ReportModel.ReportTypeChoices
        # elif report_instance.report_type == ReportModel.ReportTypeChoices.REGION_DETAIL:
        #     report_data = service.generate_region_detail_report(
        #         region_id=report_instance.region_id,
        #         start_date_str=report_instance.start_date.isoformat() if report_instance.start_date else None,
        #         end_date_str=report_instance.end_date.isoformat() if report_instance.end_date else None,
        #     )
        # ... and so on for other report types
        else:
            error_message_str = f"Report type '{report_instance.report_type}' not supported by current task logic."
            error_occurred = True
            print(f"Unsupported report type for Report ID {report_id}: {report_instance.report_type}")

        if report_data and not error_occurred:
            report_file_name = report_data.get('filename', f"report_{report_instance.id}_{report_instance.report_type.lower()}.csv")
            csv_content = report_data.get('content')

            if csv_content is not None:
                report_instance.report_file.save(report_file_name, ContentFile(csv_content.encode('utf-8')), save=False)
                # report_instance.file_format is typically set at ReportModel creation or based on service output.
                # Ensure it matches the content type if not already set.
                if not report_instance.file_format: # Default if somehow not set
                    report_instance.file_format = ReportModel.FileFormatChoices.CSV

                report_instance.status = ReportModel.StatusChoices.COMPLETED
                report_instance.summary = f"Successfully generated {report_instance.get_report_type_display()} on {timezone.now().strftime('%Y-%m-%d %H:%M')}."
                report_instance.processing_error_message = None # Clear any previous error
                print(f"Successfully generated report for Report ID {report_id}. File: {report_file_name}")
            else: # report_data exists but content is None
                error_message_str = "Report generation service returned data structure but no content."
                error_occurred = True
                print(f"No content returned for Report ID {report_id} from service.")

        elif not error_occurred: # report_data is None, and no specific error was set by type check
            error_message_str = "Report generation service returned no data (report_data is None)."
            error_occurred = True
            print(f"No data structure returned from service for Report ID {report_id}.")

    except Exception as e:
        # This catches errors from service calls or file saving
        print(f"Error during report content generation or saving for report ID {report_id}: {str(e)}")
        error_message_str = f"Failed to generate report content: {str(e)}"
        error_occurred = True
        # Re-raise the exception to allow Celery's autoretry mechanism to handle it
        raise e

    finally:
        # This block executes whether the try block succeeded or failed (and even if 'raise e' happens)
        # However, if 'raise e' is called, the task might be retried, and this 'finally'
        # might set a premature ERROR state if we are not careful.
        # The `autoretry_for` handles the retry. If all retries fail, the task state becomes FAILURE.
        # We should only update to ERROR if we are NOT re-raising for autoretry, or if this is the final state desired.
        # Given the `raise e` above, this finally block will execute, then the exception propagates.
        # If we want to ensure the DB reflects the error *after* retries, this logic needs to be in an `on_failure` handler.
        # For now, let's assume each attempt might set an error, and successful completion clears it.
        if error_occurred:
            report_instance.status = ReportModel.StatusChoices.ERROR
            report_instance.processing_error_message = error_message_str

        report_instance.updated_at = timezone.now() # Ensure updated_at is always set
        # Only save fields that are meant to be updated by this task's final state.
        update_fields_list = ['status', 'report_file', 'summary', 'processing_error_message', 'updated_at', 'file_format']
        if not report_instance.report_file: # Don't try to update report_file if it's not set
            update_fields_list.remove('report_file')
        if not report_instance.summary: # Don't try to update summary if it's not set
            update_fields_list.remove('summary')


        report_instance.save(update_fields=update_fields_list)
        print(f"Report {report_id} processing attempt finished. Final status for this attempt: {report_instance.status}")
        # If an exception was raised, Celery will retry. If no exception, this is the final result of the task.
        if error_occurred and not isinstance(e, type(None)): # Check if e is defined from an exception
             # To ensure Celery marks it as failure if we are not relying on autoretry for this specific path
             # However, the `raise e` should be the primary mechanism for autoretry.
             # This return is more of a textual status if no exception was re-raised.
            return f"Failed to generate report {report_id}. Error: {error_message_str}"
        return f"Report {report_id} generation task finished with status: {report_instance.status}"
