import json
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="UTC–Uvira | Santé & Bien-être",
    page_icon="🥤",
    layout="centered"
)

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "melanges.json"

DISCLAIMER = (
    "ℹ️ **Informations éducatives et préventives — sans se substituer à un avis médical.** "
    "Les conseils en santé naturelle sont nombreux sur les réseaux sociaux, mais souvent dispersés."
)

@st.cache_data
def load_melanges():
    if not DATA_FILE.exists():
        st.error("melanges.json introuvable dans le dépôt GitHub.")
        st.stop()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

melanges = load_melanges()

# 🔑 ICI : les objectifs viennent DIRECTEMENT du JSON
objectifs = sorted({obj for m in melanges for obj in m.get("objectifs", [])})

st.title("UTC–Uvira | Santé & Bien-être")
st.markdown(DISCLAIMER)

st.write("Objectifs détectés :", objectifs)  # ← ligne de diagnostic (temporaire)

objectif = st.selectbox(
    "Indiquez votre objectif santé :",
    objectifs
)

# Filtrage
recs = [m for m in melanges if objectif in m.get("objectifs", [])]

st.subheader("Recommandations")
if not recs:
    st.info("Aucune recommandation disponible pour cet objectif pour le moment.")
else:
    for r in recs:
        with st.container(border=True):
            st.markdown(f"### {r['nom']}")

            st.markdown("**Ingrédients**")
            st.write(", ".join(r.get("ingredients", [])))

            st.markdown("**Préparation**")
            for i, step in enumerate(r.get("preparation", []), start=1):
                st.write(f"{i}. {step}")

            if r.get("precautions"):
                st.warning(r["precautions"])
