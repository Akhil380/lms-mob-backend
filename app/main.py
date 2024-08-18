from fastapi import FastAPI
from app.api.v1.endpoints import questions,user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="LMS Mobile App Backend",
    description=(
        "This is the backend for the LMS mobile application. "
        "It includes endpoints for managing mock tests, courses, and related functionalities. "
        "can use this API to handle mock test creation, course management, and more."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api/v1", tags=["Questions Bank Upload Module"])
app.include_router(user.router, prefix="/api/v1", tags=["User Detail "])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.10", port=8000)