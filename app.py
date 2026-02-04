import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="UTC–Uvira | Santé & Bien-être", page_icon="🥤", layout="centered")

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "melanges.json"

DISCLAIMER = (
    "ℹ️ **Informations éducatives et préventives, sans se substituer à un avis médical.** "
    "Les conseils en santé naturelle sont nombreux sur les réseaux sociaux, mais souvent dispersés."
)

@st.cache_data
def load_melanges():
    if not DATA_FILE.exists():
        st.error("melanges.json introuvable. Ajoute-le au même niveau que app.py dans GitHub.")
        st.stop()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

melanges = load_melanges()

# Construire la liste d’objectifs depuis le JSON
objectifs = sorted({obj for m in melanges for obj in m.get("objectifs", [])})

st.title("UTC–Uvira | Santé & Bien-être")
st.markdown(DISCLAIMER)

selected_obj = st.selectbox(
    "Cette plateforme propose une information claire, éducative et préventive, basée sur des mélanges naturels. "
    "Indiquez votre objectif santé...",
    objectifs
)

# Filtrer les mélanges correspondant à l’objectif
recs = [m for m in melanges if selected_obj in m.get("objectifs", [])]

st.subheader("Recommandations")
if not recs:
    st.info("Aucune recommandation disponible pour cet objectif pour le moment.")
else:
    for r in recs:
        with st.container(border=True):
            st.markdown(f"### {r.get('nom', 'Sans nom')}")
            st.markdown("**Ingrédients**")
            st.write(", ".join(r.get("ingredients", [])) or "—")

            st.markdown("**Préparation**")
            steps = r.get("preparation", [])
            if steps:
                for i, s in enumerate(steps, start=1):
                    st.write(f"{i}. {s}")
            else:
                st.write("—")

            prec = r.get("precautions")
            if prec:
                st.info(f"⚠️ Précautions : {prec}")
