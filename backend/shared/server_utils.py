import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app(
    title: str, 
    version: str, 
    router=None, 
    router_prefix: str = "/api/v1", 
    router_tags: list = None
) -> FastAPI:
    """
    Create a standardized FastAPI application with common configurations.
    
    Args:
        title (str): Name of the service
        version (str): Service version
        router (Optional): Router to include
        router_prefix (str): Prefix for API routes
        router_tags (list): Tags for the router
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(title=title, version=version)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": title.lower()}

    # Include router if provided
    if router:
        app.include_router(
            router, 
            prefix=router_prefix, 
            tags=router_tags or [title.lower()]
        )

    return app

def configure_logging(log_level=logging.INFO):
    """
    Configure logging with a standard format.
    
    Args:
        log_level: Logging level, defaults to INFO
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def start_server(app: FastAPI, default_port: int):
    """
    Start the Uvicorn server with environment variable support.
    
    Args:
        app (FastAPI): FastAPI application to run
        default_port (int): Default port if not specified in environment
    """
    logger = logging.getLogger(__name__)
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", default_port))
    
    logger.info(f"Starting server on {host}:{port}")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
