from .api.routes import sensor_data
from .config import get_settings
from shared.server_utils import create_app, start_server, configure_logging

# Get settings and configure logging
settings = get_settings()
configure_logging(settings.LOG_LEVEL)

# Create FastAPI application
app = create_app(
    title="Data Service", 
    version="1.0.0", 
    router=sensor_data.router,
    router_prefix=""  # Remove the /api/v1 prefix
)

if __name__ == "__main__":
    start_server(app, default_port=8000)
