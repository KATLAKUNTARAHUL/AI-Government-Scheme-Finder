from __future__ import annotations

from typing import Any

import streamlit as st

from utils.eligibility_checker import evaluate_eligibility
from utils.pdf_generator import build_report_pdf
from utils.recommender import rank_schemes
from utils.scheme_data import load_schemes


APP_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(24, 49, 83, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(13, 148, 136, 0.16), transparent 24%),
            linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%);
    }
    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #183153 0%, #0f766e 100%);
        color: white;
        box-shadow: 0 20px 50px rgba(11, 31, 58, 0.18);
    }
    .hero h1, .hero p { margin: 0; }
    .metric-card {
        padding: 1rem 1rem 0.9rem;
        border-radius: 18px;
        background: white;
        border: 1px solid rgba(24, 49, 83, 0.08);
        box-shadow: 0 12px 30px rgba(18, 38, 63, 0.08);
    }
    .scheme-card {
        padding: 1rem 1rem 0.75rem;
        border-radius: 18px;
        background: white;
        border: 1px solid rgba(24, 49, 83, 0.1);
        box-shadow: 0 10px 24px rgba(18, 38, 63, 0.08);
        height: 100%;
    }
    .tiny-label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        color: #5c728a;
        margin-bottom: 0.25rem;
    }
    .answer {
        border-left: 4px solid #0f766e;
        padding: 0.9rem 1rem;
        background: rgba(15, 118, 110, 0.08);
        border-radius: 14px;
    }
</style>
"""


def inject_app_styles() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def _scheme_summary(scheme: dict[str, Any]) -> str:
    benefits = scheme.get("benefits") or scheme.get("description") or ""
    return str(benefits)


def _humanize(value: Any) -> str:
    return str(value or "-")


def render_dashboard() -> None:
    inject_app_styles()
    schemes = load_schemes()

    st.markdown(
        """
        <div class="hero">
            <h1>AI Government Scheme Finder</h1>
            <p>Discover eligible schemes, compare options, and export a clean summary in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    metric_columns = st.columns(4)
    metrics = [
        ("Schemes Loaded", len(schemes)),
        ("Categories", len({scheme["category"] for scheme in schemes})),
        ("State Coverage", "Pan India"),
        ("Report Export", "Enabled"),
    ]
    for column, (label, value) in zip(metric_columns, metrics, strict=False):
        with column:
            st.markdown(f'<div class="metric-card"><div class="tiny-label">{label}</div><h3>{value}</h3></div>', unsafe_allow_html=True)

    st.write("")
    st.subheader("Featured schemes")
    top_schemes = schemes[:3]
    cards = st.columns(min(3, len(top_schemes)))
    for column, scheme in zip(cards, top_schemes, strict=False):
        with column:
            st.markdown(
                f"""
                <div class="scheme-card">
                    <div class="tiny-label">{_humanize(scheme.get('category'))}</div>
                    <h4>{_humanize(scheme.get('scheme_name'))}</h4>
                    <p>{_scheme_summary(scheme)}</p>
                    <p><strong>Who it fits:</strong> {_humanize(', '.join(scheme.get('occupations') or ['Any']))}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.info("Use the sidebar to open Eligibility, Recommendations, or Chatbot.")


def render_profile_inputs(prefix: str = "profile") -> dict[str, Any]:
    defaults = {
        "age": 30,
        "income": 300000,
        "occupation": "Student",
        "state": "Any",
        "category": "General",
        "interests": "",
    }
    if "profile_defaults" not in st.session_state:
        st.session_state.profile_defaults = defaults
    defaults = {**defaults, **st.session_state.profile_defaults}

    col1, col2, col3 = st.columns(3)
    age = col1.number_input("Age", min_value=0, max_value=100, value=int(defaults["age"]), key=f"{prefix}_age")
    income = col2.number_input(
        "Annual household income",
        min_value=0,
        max_value=100000000,
        value=int(defaults["income"]),
        step=5000,
        key=f"{prefix}_income",
    )
    occupation = col3.text_input("Occupation", value=str(defaults["occupation"]), key=f"{prefix}_occupation")

    col4, col5, col6 = st.columns(3)
    state = col4.text_input("State / region", value=str(defaults["state"]), key=f"{prefix}_state")
    category = col5.text_input("Category", value=str(defaults["category"]), key=f"{prefix}_category")
    interests = col6.text_input("Interests / goals", value=str(defaults["interests"]), key=f"{prefix}_interests")

    return {
        "age": age,
        "income": income,
        "occupation": occupation,
        "state": state,
        "category": category,
        "interests": interests,
    }


def render_eligibility_page() -> None:
    inject_app_styles()
    schemes = load_schemes()

    st.title("Eligibility Checker")
    st.caption("Enter your profile once, then review every matching scheme with the reason it matched or failed.")

    with st.form("eligibility_form"):
        profile = render_profile_inputs(prefix="eligibility")
        submitted = st.form_submit_button("Check eligibility")

    if submitted:
        matched = []
        not_matched = []
        for scheme in schemes:
            result = evaluate_eligibility(profile, scheme)
            item = {**scheme, **result}
            if result["eligible"]:
                matched.append(item)
            else:
                not_matched.append(item)

        st.success(f"{len(matched)} schemes matched your profile.")
        if matched:
            for scheme in matched:
                with st.expander(f"{scheme['scheme_name']} - eligible"):
                    st.write(scheme.get("description") or scheme.get("benefits") or "")
                    st.write(f"Category: {scheme.get('category')}")
                    st.write(f"Benefits: {scheme.get('benefits')}")
                    if scheme.get("link"):
                        st.link_button("Open official page", scheme["link"])

        if not_matched:
            with st.expander("Other schemes and why they did not match"):
                for scheme in not_matched[:5]:
                    st.markdown(f"**{scheme['scheme_name']}**")
                    st.caption("; ".join(scheme["reasons"]))


def render_recommendations_page() -> None:
    inject_app_styles()
    schemes = load_schemes()

    st.title("Recommendations")
    st.caption("Ranked schemes use eligibility, occupation, category, and interest signals.")

    with st.form("recommendation_form"):
        profile = render_profile_inputs(prefix="recommendations")
        submitted = st.form_submit_button("Generate recommendations")

    if submitted:
        recommendations = rank_schemes(profile, schemes, limit=5)
        st.success("Top matches generated successfully.")

        for recommendation in recommendations:
            with st.container(border=True):
                left, right = st.columns([3, 1])
                with left:
                    st.subheader(recommendation["scheme_name"])
                    st.write(recommendation.get("description") or recommendation.get("benefits") or "")
                    st.write(f"Benefits: {recommendation.get('benefits')}")
                    if recommendation.get("reasons"):
                        st.caption("Match notes: " + "; ".join(recommendation["reasons"]) if recommendation["eligible"] else "Reasons: " + "; ".join(recommendation["reasons"]))
                with right:
                    st.metric("Score", recommendation.get("score", 0))
                    st.metric("Eligible", "Yes" if recommendation.get("eligible") else "No")
                    if recommendation.get("link"):
                        st.link_button("Open source", recommendation["link"])

        pdf_bytes = build_report_pdf(profile, recommendations)
        st.download_button(
            "Download report",
            data=pdf_bytes,
            file_name="government_scheme_report.pdf",
            mime="application/pdf",
        )


def _find_scheme_mentions(message: str, schemes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lowered = message.lower()
    matches = []
    for scheme in schemes:
        keywords = [str(keyword).lower() for keyword in (scheme.get("keywords") or [])]
        haystack = " ".join(
            [
                str(scheme.get("scheme_name") or ""),
                str(scheme.get("category") or ""),
                str(scheme.get("description") or ""),
                str(scheme.get("benefits") or ""),
                " ".join(keywords),
            ]
        ).lower()
        if scheme["scheme_name"].lower() in lowered or any(keyword in lowered for keyword in keywords) or any(token in haystack for token in lowered.split()[:3]):
            matches.append(scheme)
    return matches


def generate_chatbot_response(message: str, schemes: list[dict[str, Any]]) -> str:
    lowered = message.lower().strip()
    matched = _find_scheme_mentions(lowered, schemes)

    if any(word in lowered for word in ["hello", "hi", "help", "start"]):
        return "Ask about a scheme, or mention your age, income, occupation, and category to get a better recommendation."

    if "eligibility" in lowered or "eligible" in lowered:
        if matched:
            scheme = matched[0]
            return f"{scheme['scheme_name']} is usually for {', '.join(scheme.get('occupations') or ['broad applicants'])}. Check the Eligibility page with your profile for a precise result."
        return "Use the Eligibility page to check age, income, occupation, state, and category requirements against all loaded schemes."

    if "benefit" in lowered or "what does" in lowered or "support" in lowered:
        if matched:
            scheme = matched[0]
            return f"{scheme['scheme_name']} offers {scheme.get('benefits') or scheme.get('description') or 'scheme support'}."
        return "Tell me the scheme name, and I can summarize the benefits from the dataset."

    if "document" in lowered or "apply" in lowered:
        if matched:
            scheme = matched[0]
            return f"For {scheme['scheme_name']}, start from the official portal: {scheme.get('link') or 'official scheme website'}. Required documents depend on the scheme and state rules."
        return "Open the recommendation or eligibility result and use the official link to start the application."

    if matched:
        scheme = matched[0]
        return f"{scheme['scheme_name']} is a strong match. It belongs to {scheme.get('category')} and is aimed at {', '.join(scheme.get('occupations') or ['all applicants'])}."

    return "I can answer scheme-specific questions from the loaded dataset, or help you compare your profile against the available schemes."


def render_chatbot_page() -> None:
    inject_app_styles()
    schemes = load_schemes()

    st.title("Scheme Chatbot")
    st.caption("A lightweight assistant that answers based on the loaded scheme dataset, without needing an external API key.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello. Ask me about a scheme, its benefits, or how to start an application."}
        ]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask about a scheme")
    if user_message:
        st.session_state.chat_messages.append({"role": "user", "content": user_message})
        response = generate_chatbot_response(user_message, schemes)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()