import sqlite3
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Mélanges naturels", page_icon="🥤", layout="centered")

# Paths
APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "health_mixes.sqlite"
SEED_SQL = APP_DIR / "seed_health_mixes.sql"

DISCLAIMER = (
    "ℹ️ **Information éducative et préventive uniquement.** "
    "Cette application ne fournit pas de conseil médical."
)

def ensure_db():
    """Create SQLite DB from seed SQL if DB does not exist."""
    if DB_PATH.exists():
        return

    if not SEED_SQL.exists():
        st.error("seed_health_mixes.sql introuvable dans le dossier /app.")
        st.stop()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(SEED_SQL.read_text(encoding="utf-8"))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error("Erreur lors de la création de la base SQLite à partir du seed SQL.")
        st.exception(e)
        st.stop()

ensure_db()

@st.cache_data
def load_goals():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT code, name FROM health_goals ORDER BY name"
        ).fetchall()

def fetch_recommendations(goal_code: str, limit: int = 3):
    with sqlite3.connect(DB_PATH) as conn:
        mixes = conn.execute(
            """
            SELECT m.id, m.name, m.prep_type, m.description, m.share_slug, mg.relevance
            FROM mix_goal mg
            JOIN mixes m ON m.id = mg.mix_id
            JOIN health_goals g ON g.id = mg.goal_id
            WHERE g.code = ?
            ORDER BY mg.relevance DESC, m.name
            LIMIT ?;
            """,
            (goal_code, limit),
        ).fetchall()

        recs = []
        for mix_id, name, prep_type, desc, slug, rel in mixes:
            ings = conn.execute(
                """
                SELECT i.name
                FROM mix_ingredient mi
                JOIN ingredients i ON i.id = mi.ingredient_id
                WHERE mi.mix_id = ?
                ORDER BY i.name;
                """,
                (mix_id,),
            ).fetchall()

            warns = conn.execute(
                """
                SELECT level, message
                FROM warnings
                WHERE mix_id = ?
                ORDER BY CASE level
                    WHEN 'alerte' THEN 0
                    WHEN 'prudence' THEN 1
                    ELSE 2
                END;
                """,
                (mix_id,),
            ).fetchall()

            recs.append(
                {
                    "name": name,
                    "prep_type": prep_type,
                    "desc": desc,
                    "slug": slug,
                    "rel": rel,
                    "ingredients": [x[0] for x in ings],
                    "warnings": warns,
                }
            )
    return recs

# UI
st.title("🥤 Mélanges naturels – Santé préventive (MVP)")
st.markdown(DISCLAIMER)

# Query params for share links
q = st.query_params
goal_param = q.get("goal", None)

goals = load_goals()
if not goals:
    st.error("Aucun objectif santé trouvé dans la base de données.")
    st.stop()

goal_codes = [c for c, _ in goals]
goal_labels = {c: n for c, n in goals}

default_idx = goal_codes.index(goal_param) if goal_param in goal_codes else 0

selected_goal = st.selectbox(
    "Choisissez un objectif santé",
    goal_codes,
    format_func=lambda c: goal_labels.get(c, c),
    index=default_idx,
)

recs = fetch_recommendations(selected_goal, limit=3)

st.subheader("Recommandations")
if not recs:
    st.info("Aucune recommandation disponible pour cet objectif pour le moment.")
else:
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
                    if level == "alerte":
                        st.error(msg)
                    elif level == "prudence":
                        st.warning(msg)
                    else:
                        st.info(msg)

            share = f"{st.get_url()}?goal={selected_goal}&mix={r['slug']}"
            st.code(share, language=None)
            st.caption("Copiez ce lien pour partager.")
