from app.api.routes import upload
from config import get_settings
from shared.server_utils import create_app, start_server, configure_logging

# Get settings and configure logging
settings = get_settings()
configure_logging(settings.LOG_LEVEL)

# Create FastAPI application
app = create_app(
    title="Data Ingestion Service", 
    version="1.0.0", 
    router=upload.router
)

if __name__ == "__main__":
    start_server(app, default_port=8002)
