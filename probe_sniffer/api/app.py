from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from probe_sniffer.api.routes import devices, sightings, identities, fingerprints

app = FastAPI(
    title="probe_sniffer API",
    description="FastAPI to review and manage captured wifi probes",
    version="0.1.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router)
app.include_router(sightings.router)
app.include_router(identities.router)
app.include_router(fingerprints.router)


@app.get("/")
def root():
    return {"status": "online"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
