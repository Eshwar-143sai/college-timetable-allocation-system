from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.database.session import engine
from app.database.base_class import Base

# Create SQLite tables on startup if using SQLite
import os
if os.getenv("USE_SQLITE", "").lower() == "true":
    from sqlalchemy import text
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if column.server_default and hasattr(column.server_default, "arg"):
                arg_str = str(column.server_default.arg)
                if "ON UPDATE CURRENT_TIMESTAMP" in arg_str:
                    from sqlalchemy.sql.schema import DefaultClause
                    column.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,  # no cookie-based auth is used; keeps wildcard origin valid
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API!"}
