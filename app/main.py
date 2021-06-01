from fastapi import FastAPI, Depends

from app.routers import security, users, images

# < Development:
from fastapi.middleware.cors import CORSMiddleware
# >

from app.data.database import database
from app.data.io_files import create_folders
from app.security.methods import create_admin, get_current_active_user

app = FastAPI()

# < Development:
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# >


app.include_router(security.router)
app.include_router(users.router, dependencies=[Depends(get_current_active_user)])
app.include_router(images.router, dependencies=[Depends(get_current_active_user)])


@app.on_event("startup")
async def startup():
    await database.connect()
    await create_admin()
    await create_folders()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/ping")
async def ping():
    return {"ping": True}
