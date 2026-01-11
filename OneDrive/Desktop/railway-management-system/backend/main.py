from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stations, trains, routes, bookings, payments, admin
from app.core.database import init_db

app = FastAPI(
    title="Railway Management System",
    description="A comprehensive railway booking and management system",
    version="1.0.0"
)

# Initialize database
init_db()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "null"],  # Allow local development server and file access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(stations.router)
app.include_router(trains.router)
app.include_router(routes.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Railway Management System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)