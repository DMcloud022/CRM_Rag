import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import crm, business_card

app = FastAPI(title="Business Card Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(business_card.router)
app.include_router(crm.router)

# Remove the __main__ block
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)

# Instead, add this line at the end of the file
port = int(os.environ.get("PORT", 8000))