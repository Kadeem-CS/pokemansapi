# Pokemon FastAPI — Part 2 Submission

**Live API:** `https://your-app.onrender.com`  
**Swagger UI:** `https://your-app.onrender.com/docs`  
**ReDoc:** `https://your-app.onrender.com/redoc`

---

## Table Schema

```sql
CREATE TABLE pokemon (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    type1      VARCHAR(50)  NOT NULL,
    type2      VARCHAR(50),
    hp         INTEGER      NOT NULL,
    attack     INTEGER      NOT NULL,
    defense    INTEGER      NOT NULL,
    speed      INTEGER      NOT NULL,
    legendary  BOOLEAN      DEFAULT FALSE,
    updated_at TIMESTAMPTZ  DEFAULT NOW()
);
```

---

## Authentication

All routes require a Bearer token in the Authorization header:

```
Authorization: Bearer your-super-secret-key
```

---

## HTTP Methods — Swagger, curl, and Postman

---

### GET /pokemon — List all Pokemon

**Swagger UI:**  
1. Go to `/docs` → click `GET /pokemon` → click "Try it out"  
2. Optionally enter `type1=Fire` or `legendary=true` as query params  
3. Click Execute

**curl:**
```bash
curl -X GET "https://your-app.onrender.com/pokemon" \
  -H "Authorization: Bearer your-super-secret-key"
```

**curl with filter:**
```bash
curl -X GET "https://your-app.onrender.com/pokemon?type1=Electric&legendary=false" \
  -H "Authorization: Bearer your-super-secret-key"
```

**Postman:**
- Method: `GET`
- URL: `https://your-app.onrender.com/pokemon`
- Headers tab → Key: `Authorization` → Value: `Bearer your-super-secret-key`
- Click Send

**Expected response:**
```json
[
  { "id": 1, "name": "Bulbasaur", "type1": "Grass", "type2": "Poison",
    "hp": 45, "attack": 49, "defense": 49, "speed": 45, "legendary": false },
  ...
]
```

---

### GET /pokemon/{id} — Get one Pokemon

**curl:**
```bash
curl -X GET "https://your-app.onrender.com/pokemon/4" \
  -H "Authorization: Bearer your-super-secret-key"
```

**Expected response:**
```json
{ "id": 4, "name": "Pikachu", "type1": "Electric", "type2": null,
  "hp": 35, "attack": 55, "defense": 40, "speed": 90, "legendary": false }
```

---

### POST /pokemon — Create a new Pokemon

**Swagger UI:**  
1. Click `POST /pokemon` → "Try it out"  
2. Paste the request body below → Execute

**curl:**
```bash
curl -X POST "https://your-app.onrender.com/pokemon" \
  -H "Authorization: Bearer your-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charizard",
    "type1": "Fire",
    "type2": "Flying",
    "hp": 78,
    "attack": 84,
    "defense": 78,
    "speed": 100,
    "legendary": false
  }'
```

**Postman:**
- Method: `POST`
- URL: `https://your-app.onrender.com/pokemon`
- Headers: `Authorization: Bearer your-super-secret-key`, `Content-Type: application/json`
- Body tab → raw → JSON → paste the JSON above

**Expected response (201 Created):**
```json
{ "id": 16, "name": "Charizard", "type1": "Fire", "type2": "Flying",
  "hp": 78, "attack": 84, "defense": 78, "speed": 100, "legendary": false }
```

---

### PUT /pokemon/{id} — Fully replace a Pokemon

**curl:**
```bash
curl -X PUT "https://your-app.onrender.com/pokemon/16" \
  -H "Authorization: Bearer your-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charizard",
    "type1": "Fire",
    "type2": "Flying",
    "hp": 78,
    "attack": 109,
    "defense": 78,
    "speed": 100,
    "legendary": false
  }'
```

**Expected response:** Full updated Pokemon object.

---

### PATCH /pokemon/{id} — Partially update a Pokemon

Only send the fields you want to change.

**curl:**
```bash
curl -X PATCH "https://your-app.onrender.com/pokemon/4" \
  -H "Authorization: Bearer your-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"hp": 45, "speed": 110}'
```

**Postman:**
- Method: `PATCH`
- URL: `https://your-app.onrender.com/pokemon/4`
- Body: `{"hp": 45, "speed": 110}`

**Expected response:** Pokemon object with only hp and speed updated.

---

### DELETE /pokemon/{id} — Delete a Pokemon

**curl:**
```bash
curl -X DELETE "https://your-app.onrender.com/pokemon/16" \
  -H "Authorization: Bearer your-super-secret-key"
```

**Postman:**
- Method: `DELETE`
- URL: `https://your-app.onrender.com/pokemon/16`
- Headers: `Authorization: Bearer your-super-secret-key`

**Expected response:**
```json
{ "message": "Pokemon 16 deleted successfully" }
```

---

## Deploying to Render

1. Push all files to GitHub
2. Create new Web Service on Render → connect repo
3. Set Start Command: `uvicorn pokemon_server:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SECRET_KEY` = `your-super-secret-key`
5. Deploy — visit `/docs` to confirm
