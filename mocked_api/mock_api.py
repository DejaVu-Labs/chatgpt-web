from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import httpx

app = FastAPI()

# add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TARGET_API_BASE_URL = "https://api.openai.com"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all(request: Request, path: str):
    query_params = request.query_params
    request_url = f"{TARGET_API_BASE_URL}/{path}"

    async with httpx.AsyncClient() as client:
        request_headers = dict(request.headers)
        request_content = await request.body()

        del request_headers["host"]

        try:
            resp = await client.request(
                method=request.method,
                url=request_url,
                headers=request_headers,
                params=query_params,
                content=request_content,
                timeout=60.0
            )
            
            if "application/json" in resp.headers.get("Content-Type", ""):
                return JSONResponse(content=resp.json(), status_code=resp.status_code)
            else:
                return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
        
        except httpx.HTTPStatusError as exc:
            return JSONResponse(content={"message": "Error with request", "detail": str(exc)}, status_code=exc.response.status_code)
        except httpx.RequestError as exc:
            return JSONResponse(content={"message": "Error connecting to target API", "detail": str(exc)}, status_code=500)
        except ValueError as exc:
            return JSONResponse(content={"message": "Response parsing error", "detail": str(exc)}, status_code=500)
        except Exception as exc:
            return JSONResponse(content={"message": "An unexpected error occurred", "detail": str(exc)}, status_code=500)