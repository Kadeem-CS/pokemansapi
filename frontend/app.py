import streamlit as st
import requests
import pandas as pd
import os

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "https://pokemansapi-2.onrender.com/")
SECRET_KEY = os.getenv("SECRET_KEY", "sb_secret_qGA67gx1KVIkyZ16TywCQg_gKeFIL_o")
HEADERS = {"Authorization": f"Bearer {SECRET_KEY}"}

POKEMON_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

st.set_page_config(
    page_title="Pokédex Manager",
    page_icon="⚡",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #FFCB05;
        text-shadow: 2px 2px 4px #3B4CCA;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #3B4CCA 0%, #2a3890 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        color: white;
    }
    .type-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background: #3B4CCA;
        color: white;
        margin: 2px;
    }
    .success-msg { color: #28a745; font-weight: 600; }
    .error-msg   { color: #dc3545; font-weight: 600; }
    div[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ───────────────────────────────────────────────────────────────
def api_get(path: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{path}", headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_post(path: str, body: dict):
    try:
        r = requests.post(f"{API_URL}{path}", headers=HEADERS, json=body, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_put(path: str, body: dict):
    try:
        r = requests.put(f"{API_URL}{path}", headers=HEADERS, json=body, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_patch(path: str, body: dict):
    try:
        r = requests.patch(f"{API_URL}{path}", headers=HEADERS, json=body, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def api_delete(path: str):
    try:
        r = requests.delete(f"{API_URL}{path}", headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return None, detail
    except Exception as e:
        return None, str(e)

def fetch_all():
    data, err = api_get("/pokemon")
    return data or [], err

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">⚡ Pokédex Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Search · Create · Retrieve · Update · Delete</div>', unsafe_allow_html=True)

# Health check banner
health, err = api_get("/health")
if err:
    st.warning(f"⏳ API is waking up, please wait 30 seconds and refresh the page.")
else:
    st.success(f"✅ Connected to API: `{API_URL}`")
    
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_search, tab_retrieve, tab_create, tab_update, tab_delete = st.tabs([
    "🔍 Search", "📋 Retrieve", "➕ Create", "✏️ Update", "🗑️ Delete"
])


# ════════════════════════════════════════════════════════════
#  SEARCH
# ════════════════════════════════════════════════════════════
with tab_search:
    st.subheader("Search Pokémon")
    st.caption("Filter the full Pokédex by type and legendary status.")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_type = st.selectbox("Filter by Type", ["(All)"] + POKEMON_TYPES, key="search_type")
    with col2:
        filter_legendary = st.selectbox("Legendary Status", ["(All)", "Legendary only", "Non-legendary only"], key="search_leg")
    with col3:
        st.write("")
        st.write("")
        search_btn = st.button("Search", type="primary", use_container_width=True)

    if search_btn or True:   # always show on load
        params = {}
        if filter_type != "(All)":
            params["type1"] = filter_type
        if filter_legendary == "Legendary only":
            params["legendary"] = "true"
        elif filter_legendary == "Non-legendary only":
            params["legendary"] = "false"

        data, err = api_get("/pokemon", params=params)
        if err:
            st.error(f"Error: {err}")
        elif not data:
            st.info("No Pokémon found matching those filters.")
        else:
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Results", len(data))
            m2.metric("Legendary", sum(1 for p in data if p.get("legendary")))
            m3.metric("Avg HP", round(sum(p["hp"] for p in data) / len(data)))
            m4.metric("Avg Speed", round(sum(p["speed"] for p in data) / len(data)))

            # Table
            df = pd.DataFrame(data)
            display_cols = ["id", "name", "type1", "type2", "hp", "attack", "defense", "speed", "legendary"]
            df = df[[c for c in display_cols if c in df.columns]]
            df["legendary"] = df["legendary"].apply(lambda x: "⭐ Yes" if x else "No")
            df["type2"] = df["type2"].fillna("—")
            st.dataframe(df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════
#  RETRIEVE
# ════════════════════════════════════════════════════════════
with tab_retrieve:
    st.subheader("Retrieve a Single Pokémon")
    st.caption("Look up full stats for one Pokémon by ID.")

    col1, col2 = st.columns([2, 1])
    with col1:
        retrieve_id = st.number_input("Pokémon ID", min_value=1, step=1, key="retrieve_id")
    with col2:
        st.write("")
        st.write("")
        retrieve_btn = st.button("Retrieve", type="primary", use_container_width=True)

    if retrieve_btn:
        data, err = api_get(f"/pokemon/{int(retrieve_id)}")
        if err:
            st.error(f"Error: {err}")
        else:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"### #{data['id']} {data['name']}")
                types = f"`{data['type1']}`"
                if data.get("type2"):
                    types += f"  `{data['type2']}`"
                st.markdown(f"**Type:** {types}")
                st.markdown(f"**Legendary:** {'⭐ Yes' if data['legendary'] else 'No'}")
            with c2:
                stats = {
                    "HP": data["hp"],
                    "Attack": data["attack"],
                    "Defense": data["defense"],
                    "Speed": data["speed"]
                }
                for stat, val in stats.items():
                    pct = min(val / 200, 1.0)
                    st.markdown(f"**{stat}** — {val}")
                    st.progress(pct)


# ════════════════════════════════════════════════════════════
#  CREATE
# ════════════════════════════════════════════════════════════
with tab_create:
    st.subheader("Create a New Pokémon")
    st.caption("Add a new Pokémon to the database via POST /pokemon.")

    with st.form("create_form"):
        c1, c2 = st.columns(2)
        with c1:
            name     = st.text_input("Name *", placeholder="e.g. Charizard")
            type1    = st.selectbox("Primary Type *", POKEMON_TYPES)
            type2    = st.selectbox("Secondary Type (optional)", ["(None)"] + POKEMON_TYPES)
            legendary = st.checkbox("Legendary?")
        with c2:
            hp       = st.slider("HP",      1, 255, 45)
            attack   = st.slider("Attack",  1, 255, 50)
            defense  = st.slider("Defense", 1, 255, 50)
            speed    = st.slider("Speed",   1, 255, 50)

        submitted = st.form_submit_button("➕ Create Pokémon", type="primary")

    if submitted:
        if not name.strip():
            st.error("Name is required.")
        else:
            body = {
                "name": name.strip(),
                "type1": type1,
                "type2": type2 if type2 != "(None)" else None,
                "hp": hp, "attack": attack, "defense": defense, "speed": speed,
                "legendary": legendary
            }
            data, err = api_post("/pokemon", body)
            if err:
                st.error(f"Failed to create: {err}")
            else:
                st.success(f"✅ Created **{data['name']}** with ID `{data['id']}`!")
                st.json(data)


# ════════════════════════════════════════════════════════════
#  UPDATE
# ════════════════════════════════════════════════════════════
with tab_update:
    st.subheader("Update a Pokémon")
    st.caption("Load a Pokémon by ID, edit any fields, then save via PATCH /pokemon/{id}.")

    col1, col2 = st.columns([2, 1])
    with col1:
        update_id = st.number_input("Pokémon ID to update", min_value=1, step=1, key="update_id")
    with col2:
        st.write("")
        st.write("")
        load_btn = st.button("Load Pokémon", use_container_width=True)

    if load_btn:
        data, err = api_get(f"/pokemon/{int(update_id)}")
        if err:
            st.error(f"Error: {err}")
        else:
            st.session_state["loaded_pokemon"] = data
            st.success(f"Loaded: **{data['name']}**")

    if "loaded_pokemon" in st.session_state:
        p = st.session_state["loaded_pokemon"]
        st.markdown(f"**Editing:** #{p['id']} — {p['name']}")

        with st.form("update_form"):
            c1, c2 = st.columns(2)
            with c1:
                u_name  = st.text_input("Name", value=p["name"])
                t1_idx  = POKEMON_TYPES.index(p["type1"]) if p["type1"] in POKEMON_TYPES else 0
                u_type1 = st.selectbox("Primary Type", POKEMON_TYPES, index=t1_idx)
                t2_opts = ["(None)"] + POKEMON_TYPES
                t2_idx  = t2_opts.index(p["type2"]) if p.get("type2") in t2_opts else 0
                u_type2 = st.selectbox("Secondary Type", t2_opts, index=t2_idx)
                u_leg   = st.checkbox("Legendary?", value=p.get("legendary", False))
            with c2:
                u_hp      = st.slider("HP",      1, 255, int(p["hp"]))
                u_attack  = st.slider("Attack",  1, 255, int(p["attack"]))
                u_defense = st.slider("Defense", 1, 255, int(p["defense"]))
                u_speed   = st.slider("Speed",   1, 255, int(p["speed"]))

            save_btn = st.form_submit_button("💾 Save Changes", type="primary")

        if save_btn:
            body = {
                "name": u_name.strip(),
                "type1": u_type1,
                "type2": u_type2 if u_type2 != "(None)" else None,
                "hp": u_hp, "attack": u_attack,
                "defense": u_defense, "speed": u_speed,
                "legendary": u_leg
            }
            data, err = api_patch(f"/pokemon/{p['id']}", body)
            if err:
                st.error(f"Update failed: {err}")
            else:
                st.success(f"✅ Updated **{data['name']}** successfully!")
                st.session_state["loaded_pokemon"] = data
                st.json(data)


# ════════════════════════════════════════════════════════════
#  DELETE
# ════════════════════════════════════════════════════════════
with tab_delete:
    st.subheader("Delete a Pokémon")
    st.caption("Permanently remove a Pokémon from the database via DELETE /pokemon/{id}.")

    del_id = st.number_input("Pokémon ID to delete", min_value=1, step=1, key="del_id")

    preview_btn = st.button("Preview Pokémon", key="preview_del")
    if preview_btn:
        data, err = api_get(f"/pokemon/{int(del_id)}")
        if err:
            st.error(f"Error: {err}")
        else:
            st.session_state["delete_preview"] = data

    if "delete_preview" in st.session_state:
        p = st.session_state["delete_preview"]
        st.warning(
            f"⚠️ You are about to delete **#{p['id']} {p['name']}** "
            f"({p['type1']}{' / ' + p['type2'] if p.get('type2') else ''}) — this cannot be undone."
        )
        confirm = st.checkbox("I confirm I want to delete this Pokémon")
        if confirm:
            if st.button("🗑️ Delete Permanently", type="primary"):
                result, err = api_delete(f"/pokemon/{p['id']}")
                if err:
                    st.error(f"Delete failed: {err}")
                else:
                    st.success(f"✅ {result['message']}")
                    del st.session_state["delete_preview"]

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem;'>"
    "Pokédex Manager · FastAPI + Supabase backend · Streamlit frontend"
    "</div>",
    unsafe_allow_html=True
)
