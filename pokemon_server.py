from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import create_client, Client
from typing import Optional
from datetime import datetime, timezone
import os

app = FastAPI(
    title="Pokemon API",
    description="A RESTful API to manage Pokemon using FastAPI + Supabase",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth ──────────────────────────────────────────────────────────────────────
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials.credentials

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL environment variable")
if not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_KEY environment variable")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Pydantic Models ───────────────────────────────────────────────────────────
class PokemonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Pikachu")
    type1: str = Field(..., min_length=1, max_length=50, example="Electric")
    type2: Optional[str] = Field(None, max_length=50, example=None)
    hp: int = Field(..., ge=1, le=999, example=35)
    attack: int = Field(..., ge=1, le=999, example=55)
    defense: int = Field(..., ge=1, le=999, example=40)
    speed: int = Field(..., ge=1, le=999, example=90)
    legendary: bool = Field(default=False, example=False)


class PokemonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type1: Optional[str] = Field(None, min_length=1, max_length=50)
    type2: Optional[str] = Field(None, max_length=50)
    hp: Optional[int] = Field(None, ge=1, le=999)
    attack: Optional[int] = Field(None, ge=1, le=999)
    defense: Optional[int] = Field(None, ge=1, le=999)
    speed: Optional[int] = Field(None, ge=1, le=999)
    legendary: Optional[bool] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check — returns total Pokemon count."""
    response = supabase.table("pokemon").select("*", count="exact").execute()
    return {
        "message": "Pokemon API is running!",
        "total_pokemon": response.count
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/pokemon", tags=["Pokemon"])
async def list_pokemon(
    type1: Optional[str] = None,
    legendary: Optional[bool] = None,
    token: str = Depends(verify_token)
):
    """
    Get all Pokemon. Optionally filter by:
    - **type1**: e.g. `Fire`, `Water`, `Electric`
    - **legendary**: `true` or `false`
    """
    query = supabase.table("pokemon").select("*").order("id")
    if type1:
        query = query.ilike("type1", type1)
    if legendary is not None:
        query = query.eq("legendary", legendary)
    response = query.execute()
    return response.data


@app.get("/pokemon/{pokemon_id}", tags=["Pokemon"])
async def get_pokemon(pokemon_id: int, token: str = Depends(verify_token)):
    """Get a single Pokemon by ID."""
    response = (
        supabase.table("pokemon")
        .select("*")
        .eq("id", pokemon_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Pokemon with id {pokemon_id} not found")
    return response.data[0]


@app.post("/pokemon", status_code=201, tags=["Pokemon"])
async def create_pokemon(pokemon: PokemonCreate, token: str = Depends(verify_token)):
    """Create a new Pokemon record."""
    payload = pokemon.model_dump()
    payload["updated_at"] = utc_now()

    response = supabase.table("pokemon").insert(payload).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create Pokemon")
    return response.data[0]


@app.put("/pokemon/{pokemon_id}", tags=["Pokemon"])
async def replace_pokemon(
    pokemon_id: int,
    pokemon: PokemonCreate,
    token: str = Depends(verify_token)
):
    """Fully replace a Pokemon record (all fields required)."""
    payload = pokemon.model_dump()
    payload["updated_at"] = utc_now()

    response = (
        supabase.table("pokemon")
        .update(payload)
        .eq("id", pokemon_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Pokemon with id {pokemon_id} not found")
    return response.data[0]


@app.patch("/pokemon/{pokemon_id}", tags=["Pokemon"])
async def update_pokemon(
    pokemon_id: int,
    pokemon: PokemonUpdate,
    token: str = Depends(verify_token)
):
    """Partially update a Pokemon record (only send fields you want to change)."""
    update_data = pokemon.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_data["updated_at"] = utc_now()

    response = (
        supabase.table("pokemon")
        .update(update_data)
        .eq("id", pokemon_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Pokemon with id {pokemon_id} not found")
    return response.data[0]


@app.delete("/pokemon/{pokemon_id}", tags=["Pokemon"])
async def delete_pokemon(pokemon_id: int, token: str = Depends(verify_token)):
    """Delete a Pokemon by ID."""
    response = (
        supabase.table("pokemon")
        .delete()
        .eq("id", pokemon_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Pokemon with id {pokemon_id} not found")
    return {"message": f"Pokemon {pokemon_id} deleted successfully"}
