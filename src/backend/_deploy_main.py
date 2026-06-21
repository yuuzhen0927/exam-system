import uvicorn, os
from main import app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

dist = r"F:\CodexWorkspace\Project004_考试系统\src\frontend\dist"
if os.path.isdir(dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist, "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist, "index.html"))

uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
