from celery import shared_task
import ee

@shared_task
def initialize_and_fetch_gee_image(region_name, start_date, end_date):
    credentials = ee.ServiceAccountCredentials.from_p12(
        email=os.getenv('GEE_SERVICE_ACCOUNT'),
        key_file=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        scopes=['https://www.googleapis.com/auth/earthengine']
    )
    ee.Initialize(credentials)

    zanzan_geometry = ee.Geometry.Rectangle([-3.5, 7.5, -2.5, 8.5])  # Bondoukou approx.
    collection = (ee.ImageCollection('COPERNICUS/S2')
                  .filterDate(start_date, end_date)
                  .filterBounds(zanzan_geometry)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .first())
    # Logique pour sauvegarder l'image dans ImageModel (à implémenter)