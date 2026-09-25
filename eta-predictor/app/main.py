import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import ETARequest, ETAResponse, HealthResponse
from app.predictor import ETAPredictor


app = FastAPI(
    title="ETA Predictor API",
    description="""
    Production-grade logistics ETA prediction service.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

predictor = ETAPredictor()
START_TIME = time.time()



@app.on_event('startup')
async def load_model_on_startup():
    """Load the ML model when the server starts."""
    success = predictor.load()
    if not success:
        print('WARNING: API starting without a loaded model.')
        print('POST /predict will return 503 until a model is loaded.')


@app.get('/', include_in_schema=False)
async def root():
    return {"message": "ETA Predictor API", "docs": "/docs"}


@app.get('/health', response_model=HealthResponse, tags=['System'])
async def health_check():
    """
    Check if the API and ML model are healthy.
    Returns 'healthy' if the model is loaded, 'degraded' if not.
    """
    return HealthResponse(
        status='healthy' if predictor.is_loaded else 'degraded',
        model_loaded=predictor.is_loaded,
        api_version='1.0.0',
    )


@app.post('/predict', response_model=ETAResponse, tags=['Predictions'])
async def predict_eta(request: ETARequest):
    """
    Predict the estimated delivery time.

    Provide origin/destination GPS coordinates, cargo details, and departure time.
    Returns estimated delivery time in minutes plus a confidence interval.
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Model not loaded. Check server logs.',
        )
    try:
        features = request.to_feature_vector()
        eta_min, ci_low, ci_high = predictor.predict(features)

        hours   = int(eta_min // 60)
        minutes = int(eta_min % 60)
        hour_label = 'hour' if hours == 1 else 'hours'
        minute_label = 'minute' if minutes == 1 else 'minutes'
        if hours > 0:
            eta_human = f'{hours} {hour_label} {minutes} {minute_label}'
        else:
            eta_human = f'{minutes} {minute_label}'

        return ETAResponse(
            eta_minutes=eta_min,
            eta_human_readable=eta_human,
            distance_km=request.distance_km,
            confidence_low=ci_low,
            confidence_high=ci_high,
            is_rush_hour=request.is_rush_hour,
            model_version=predictor.version,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Prediction failed: {str(e)}',
        )
