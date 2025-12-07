from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from probe_sniffer import config
from probe_sniffer.api.discord_bot import bot
from probe_sniffer.api.routes import devices, sightings, identities, fingerprints
from probe_sniffer.api.schemas import NotifyRequest

logger = logging.getLogger("API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Discord bot as background task
    if config.DISCORD_BOT_TOKEN:
        logger.info(f"Starting Discord bot (token: {config.DISCORD_BOT_TOKEN[:10]}...)")
        asyncio.create_task(bot.start(config.DISCORD_BOT_TOKEN))
    else:
        logger.warning("DISCORD_BOT_TOKEN not set, bot will not start")
    yield
    logger.info("Shutting down Discord bot...")
    await bot.close()


app = FastAPI(
    title="probe_sniffer API",
    description="FastAPI to review and manage captured wifi probes",
    version="0.1.0",
    lifespan=lifespan,
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


@app.post("/internal/notify")
async def notify(payload: NotifyRequest):
    logger.info(f"Notify request: type={payload.notification_type}, fingerprint={payload.fingerprint.get('fingerprint_id', 'unknown')[:16]}...")
    try:
        await bot.send_notification(payload.fingerprint, payload.probe_data, payload.notification_type)
        return {"status": "sent"}
    except Exception as e:
        logger.error(f"Failed to send notification: {e}", exc_info=True)
        raise
