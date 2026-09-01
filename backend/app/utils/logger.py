import logging
import sys

def setup_logging():
    # Simple structured-like logging to standard output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Mute noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
