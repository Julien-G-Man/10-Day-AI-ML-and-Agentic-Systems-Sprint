
import time, logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SatelliteReportRequest, SatelliteReportResponse
from app.agent import build_satellite_agent

logging.basicConfig(level=logging.INFO)
app = FastAPI(title='Satellite Intelligence Agent API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'],
allow_headers=['*'])

_agent = None

@app.on_event('startup')
async def startup():
    global _agent
    _agent = build_satellite_agent(verbose=False)
    logging.info('Satellite agent ready')

@app.get("/")
async def root():
    return {'status': 'ok', 'message': 'Satellite Intelligence Agent API'}

@app.get('/health')
async def health():
    return {'status': 'healthy', 'agent': 'ready'} if _agent else {'status': 'degraded'}

@app.post('/satellite-report', response_model=SatelliteReportResponse)
async def satellite_report(req: SatelliteReportRequest):
    if not _agent:
        raise HTTPException(503, 'Agent not ready')
    t0 = time.time()
    try:
        query = f'Generate a complete intelligence report on {req.satellite_name}.'
        if not req.include_news:
            query += ' Skip the news search, focus on technical data only.'
        result = _agent.invoke({'input': query})
        messages = result.get('messages', [])
        # Count tool invocations by checking for a tool_call_id attribute on tool messages
        steps_taken = 0
        for m in messages:
            try:
                if getattr(m, 'tool_call_id', None) is not None:
                    steps_taken += 1
            except Exception:
                continue

        return SatelliteReportResponse(
            satellite_name=req.satellite_name,
            report=result.get('output'),
            steps_taken=steps_taken,
            latency_ms=round((time.time()-t0)*1000, 1),
        )
    except Exception as e:
        raise HTTPException(500, str(e))
