from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.db import engine, Base
from app.routers import auth, projects, admin, contracts, finance, helpdesk, qa, safety, library, hr, recruitment, tasks, leave_request, timesheet, contact_directory, ticket, cute
from app.routers.schedule import router as schedule_router
from app.routers.files_ext import router as files_ext_router
from app.routers.usersprofile import router as userprofile

app = FastAPI(title=config.app.name, debug=config.app.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers (each only once)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(admin.router)
app.include_router(contracts.router)
app.include_router(finance.router)
app.include_router(helpdesk.router)
app.include_router(qa.router)
app.include_router(safety.router)
app.include_router(library.router)
app.include_router(hr.router)
app.include_router(recruitment.router)
app.include_router(tasks.router)
app.include_router(schedule_router)
app.include_router(files_ext_router)
app.include_router(userprofile)
app.include_router(leave_request.router)
app.include_router(timesheet.router)
app.include_router(ticket.router)
app.include_router(contact_directory.router)
app.include_router(cute.router)

@app.get("/health")
def health():
    return {"ok": True}




app.include_router(projects.router)

app.include_router(tasks.router)

app.include_router(schedule_router)
app.include_router(files_ext_router)
