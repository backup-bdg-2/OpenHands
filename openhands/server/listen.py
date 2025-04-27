import os

import socketio

from openhands.server.app import app as base_app
from openhands.server.listen_socket import sio
from openhands.server.middleware import (
    AttachConversationMiddleware,
    CacheControlMiddleware,
    InMemoryRateLimiter,
    LocalhostCORSMiddleware,
    RateLimitMiddleware,
)
from openhands.server.static import SPAStaticFiles

if os.getenv('SERVE_FRONTEND', 'true').lower() == 'true':
    frontend_dir = './frontend/build'
    if os.path.exists(frontend_dir):
        base_app.mount(
            '/', SPAStaticFiles(directory=frontend_dir, html=True), name='dist'
        )
    else:
        print(f"Warning: Frontend directory '{frontend_dir}' does not exist. Not serving frontend files.")

base_app.add_middleware(
    LocalhostCORSMiddleware,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

base_app.add_middleware(CacheControlMiddleware)
base_app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=InMemoryRateLimiter(requests=10, seconds=1),
)
base_app.middleware('http')(AttachConversationMiddleware(base_app))

app = socketio.ASGIApp(sio, other_asgi_app=base_app)
