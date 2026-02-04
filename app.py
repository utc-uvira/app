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
        st.error("melanges.json introuvable. Ajoute-le au même niveau que app.py dans GitHub.")
        st.stop()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            st.error("melanges.json doit contenir une LISTE d’objets (entre [ ... ]).")
            st.stop()
        return data
    except json.JSONDecodeError as e:
        st.error("melanges.json contient une erreur de format (JSON invalide).")
        st.exception(e)
        st.stop()

melanges = load_melanges()
st.write("Nombre de mélanges chargés :", len(melanges))
st.write("IDs chargés :", sorted([m.get("id") for m in melanges if isinstance(m, dict)]))

# Objectifs uniques
objectifs = sorted({obj for m in melanges for obj in m.get("objectifs", []) if isinstance(obj, str)})

st.title("UTC–Uvira | Santé & Bien-être")
st.markdown(DISCLAIMER)

if not objectifs:
    st.error("Aucun objectif détecté dans melanges.json (champ 'objectifs').")
    st.stop()

objectif = st.selectbox("Indiquez votre objectif santé :", objectifs)

# Filtrer les mélanges
recs = [m for m in melanges if objectif in m.get("objectifs", [])]

st.subheader("Recommandations")
if not recs:
    st.info("Aucune recommandation disponible pour cet objectif pour le moment.")
else:
    for r in recs:
        with st.container(border=True):
            nom = r.get("nom", "Sans nom")
            st.markdown(f"### {nom}")

            # Ingrédients
            ingredients = r.get("ingredients", [])
            if isinstance(ingredients, str):
                ingredients = [ingredients]
            if not isinstance(ingredients, list):
                ingredients = []

            st.markdown("**Ingrédients**")
            st.write(", ".join(ingredients) if ingredients else "—")

            # Préparation
            preparation = r.get("preparation", [])
            if isinstance(preparation, str):
                preparation = [preparation]
            if not isinstance(preparation, list):
                preparation = []

            st.markdown("**Préparation**")
            if preparation:
                for i, step in enumerate(preparation, start=1):
                    st.write(f"{i}. {step}")
            else:
                st.write("—")

            # Précautions
            precautions = r.get("precautions", "")
            if precautions:
                st.warning(precautions)
