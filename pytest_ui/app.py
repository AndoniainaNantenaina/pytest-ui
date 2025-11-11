from parser import parse_pytest_report
from pathlib import Path

import pandas as pd
import streamlit as st
from runner import PytestRunner

st.set_page_config(page_title="Pytest UI", layout="wide")

# --- Sidebar ---
st.sidebar.header("⚙️ Paramètres")
project_path = st.sidebar.text_input("Dossier de tests", value="./tests")
keyword = st.sidebar.text_input("Filtre (-k)", placeholder="mot_clé optionnel")
run_button = st.sidebar.button("🚀 Lancer les tests")

# --- État session ---
if "results" not in st.session_state:
    st.session_state["results"] = []

status_header = st.empty()

# --- Lancement des tests ---
if run_button:
    runner = PytestRunner(Path(project_path))
    status_header.info("⏳ Exécution en cours...")
    output = runner.run_tests(keyword=keyword)
    report = output.get("report")

    if not report:
        status_header.error("Aucun rapport JSON trouvé !")
    else:
        results = parse_pytest_report(report)
        st.session_state["results"] = results

    status_header.empty()

# --- Affichage des résultats ---
results = st.session_state["results"]

if results:
    df = pd.DataFrame([r.__dict__ for r in results])
    passed = len(df[df["outcome"] == "passed"])
    failed = len(df[df["outcome"] == "failed"])
    total = len(df)

    c1, c2, c3 = st.columns(3, width="stretch")
    with c1:
        st.metric("✅ PASSED", passed)
    with c2:
        st.metric("❌ FAILED", failed)
    with c3:
        st.metric("🧪 TOTAL", total)

    st.divider()

    df["nodeid"] = df["nodeid"].astype(str).str.split("::").str[0]
    df["outcome"] = df["outcome"].astype(str).str.upper()
    df["outcome"] = df["outcome"].replace(
        {
            "PASSED": "✅",
            "FAILED": "❌",
            "SKIPPED": "🟡",
        }
    )

    grouped = df.groupby("nodeid")
    for outcome, group in grouped:
        group_failed_len = len(group[group["outcome"] == "❌"])
        group_passed_len = len(group[group["outcome"] == "✅"])

        with st.expander(
            f"""
*{outcome} ({len(group)})*
- **PASSED:{group_passed_len}** // **FAILED:{group_failed_len}**
            """,
        ):
            group = group.set_index("outcome")
            st.dataframe(group, use_container_width=True)

    selected = st.selectbox("Afficher les logs d'un test :", df["name"])
    test = df[df["name"] == selected].iloc[0]
    st.code(
        test["message"] or "Aucun message.",
        language="bash",
        line_numbers=True,
        height="content",
    )
else:
    st.warning("Aucun test exécuté pour le moment.")
