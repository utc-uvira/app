import sqlite3
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Mélanges naturels", page_icon="🥤", layout="centered")

DB_PATH = Path(__file__).parent / "health_mixes.sqlite"

DISCLAIMER = ("ℹ️ **Information éducative et préventive uniquement.** "
              "Cette application ne fournit pas de conseil médical.")

@st.cache_data
def load_goals():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT code, name FROM health_goals ORDER BY name").fetchall()

def fetch_recommendations(goal_code, limit=3):
    with sqlite3.connect(DB_PATH) as conn:
        mixes = conn.execute("""
            SELECT m.id, m.name, m.prep_type, m.description, m.share_slug, mg.relevance
            FROM mix_goal mg
            JOIN mixes m ON m.id = mg.mix_id
            JOIN health_goals g ON g.id = mg.goal_id
            WHERE g.code = ?
            ORDER BY mg.relevance DESC, m.name
            LIMIT ?;
        """, (goal_code, limit)).fetchall()

        recs = []
        for mix_id, name, prep_type, desc, slug, rel in mixes:
            ings = conn.execute("""
                SELECT i.name
                FROM mix_ingredient mi
                JOIN ingredients i ON i.id = mi.ingredient_id
                WHERE mi.mix_id = ?
                ORDER BY i.name;
            """, (mix_id,)).fetchall()

            warns = conn.execute("""
                SELECT level, message
                FROM warnings
                WHERE mix_id = ?
                ORDER BY CASE level WHEN 'alerte' THEN 0 WHEN 'prudence' THEN 1 ELSE 2 END;
            """, (mix_id,)).fetchall()

            recs.append({
                "name": name,
                "prep_type": prep_type,
                "desc": desc,
                "slug": slug,
                "rel": rel,
                "ingredients": [x[0] for x in ings],
                "warnings": warns
            })
    return recs

st.title("🥤 Mélanges naturels – Santé préventive (MVP)")
st.markdown(DISCLAIMER)

# Lire paramètres d’URL pour partage
q = st.query_params
goal_param = q.get("goal", None)

goals = load_goals()
goal_codes = [c for c,_ in goals]
goal_labels = {c:n for c,n in goals}

default_idx = goal_codes.index(goal_param) if goal_param in goal_codes else 0
selected_goal = st.selectbox("Choisissez un objectif santé", goal_codes,
                             format_func=lambda c: goal_labels.get(c, c),
                             index=default_idx)

recs = fetch_recommendations(selected_goal, limit=3)

for r in recs:
    with st.container(border=True):
        st.markdown(f"### {r['name']}")
        st.caption(f"Type: **{r['prep_type']}** · Pertinence: **{r['rel']}**")
        if r["desc"]:
            st.write(r["desc"])
        st.markdown("**Ingrédients**")
        st.write(", ".join(r["ingredients"]) if r["ingredients"] else "—")

        if r["warnings"]:
            st.markdown("**Précautions**")
            for level, msg in r["warnings"]:
                (st.error if level=="alerte" else st.warning if level=="prudence" else st.info)(msg)

        # Lien partageable vers Streamlit (objectif + mix)
        share = f"{st.get_url()}?goal={selected_goal}&mix={r['slug']}"
        st.code(share, language=None)
