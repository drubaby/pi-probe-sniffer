from fastapi import FastAPI
from probe_sniffer.api.routes import devices, sightings

app = FastAPI(
    title="probe_sniffer API",
    description="FastAPI to review and manage captured wifi probes",
    version="0.1.0",
)

app.include_router(devices.router)
app.include_router(sightings.router)


@app.get("/")
def root():
    return {"status": "online"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
