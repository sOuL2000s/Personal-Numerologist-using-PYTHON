"""
Streamlit front-end for the Detailed Numerology Analyzer.
Run locally:  streamlit run streamlit_app.py
Deploy:       Streamlit Community Cloud / Hugging Face Spaces
"""

import io
import os
import datetime

import streamlit as st

# ---- Import all your numerology logic from the existing module ----
import numerology as nm


# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Detailed Numerology Analyzer",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------
# Custom CSS for a clean look
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1a1a2e;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1rem;
            color: #555;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .section-head {
            font-size: 1.25rem;
            font-weight: 700;
            color: #16213e;
            margin-top: 1.5rem;
            margin-bottom: 0.4rem;
        }
        .num-head {
            font-size: 1.05rem;
            font-weight: 600;
            color: #0f3460;
            margin-top: 1rem;
        }
        .disclaimer {
            font-size: 0.8rem;
            color: #777;
            border-top: 1px solid #ddd;
            padding-top: 0.8rem;
            margin-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Helpers to build the report dict (mirrors generate_report in numerology.py)
# ---------------------------------------------------------------------
def build_report_dict(name: str, dob: str) -> dict:
    """Compute everything and return the same dict generate_pdf_report expects."""
    lp, m_r, d_r, y_r, lp_total = nm.life_path(dob)
    bd = nm.birth_day_number(dob)
    expr, expr_raw = nm.expression_number(name)
    soul, soul_raw = nm.soul_urge_number(name)
    pers, pers_raw = nm.personality_number(name)
    mat = nm.maturity_number(lp, expr)
    bal = nm.balance_number(name)
    kd = nm.karmic_debts(dob, name)
    kl = nm.karmic_lessons(name)
    hp = nm.hidden_passion(name)
    ss = nm.subconscious_self(name)
    planes = nm.planes_of_expression(name)
    pins = nm.pinnacles(dob)
    chals = nm.challenges(dob)
    cycles = nm.life_cycles(dob)
    py = nm.personal_year(dob)

    report = {
        "name": name,
        "dob": f"{dob[0:2]}/{dob[2:4]}/{dob[4:8]}",
        "core": [],
        "synthesis": [],
        "areas": [],
        "karmic_debts": [],
        "karmic_lessons": [],
        "hidden_passion": [],
        "subconscious": "",
        "planes": planes,
        "pinnacles": [],
        "challenges": [],
        "cycles": [],
        "personal_year": None,
        "blunt": {},
        "disclaimer": (
            "Numerology is a symbolic system for reflection and entertainment. "
            "It is not a substitute for professional psychological, medical, "
            "financial, or legal advice. The 'truths' here are archetypal "
            "patterns — take what resonates, leave what doesn't."
        ),
    }

    # Core numbers
    report["core"].append(("Life Path", lp, nm.NUMEROLOGY_DESCRIPTIONS.get(lp, ""),
        [f"Calculation: Month {m_r} + Day {d_r} + Year {y_r} = {lp_total} → {lp}"]))
    report["core"].append(("Expression / Destiny", expr,
        nm.NUMEROLOGY_DESCRIPTIONS.get(expr, ""), None))
    report["core"].append(("Soul Urge / Heart's Desire", soul,
        nm.NUMEROLOGY_DESCRIPTIONS.get(soul, ""), None))
    report["core"].append(("Personality", pers,
        nm.NUMEROLOGY_DESCRIPTIONS.get(pers, ""), None))
    report["core"].append(("Birth Day", bd,
        nm.NUMEROLOGY_DESCRIPTIONS.get(bd, ""), None))
    report["core"].append(("Maturity", mat,
        nm.NUMEROLOGY_DESCRIPTIONS.get(mat, ""), None))
    report["core"].append(("Balance", bal,
        "The number you invoke under stress to regain equilibrium.", None))

    # Synthesis
    numbers = {
        "Life Path": lp, "Birth Day": bd, "Expression": expr,
        "Soul Urge": soul, "Personality": pers, "Maturity": mat,
        "Balance": bal,
    }
    for insight in nm.synthesize(numbers):
        report["synthesis"].append(insight)

    # Areas
    area_titles = {
        "career": "CAREER & PURPOSE",
        "money": "MONEY & FINANCES",
        "love": "LOVE & RELATIONSHIPS",
        "health": "HEALTH & ENERGY",
        "spirituality": "SPIRITUALITY & GROWTH",
        "shadow": "SHADOW & BLIND SPOTS",
        "advice": "DIRECT ADVICE",
    }
    for area in area_titles:
        entries = []
        entries.append(("Life Path", nm.advice_for_number(lp, area)))
        if nm.reduce_full(expr) != nm.reduce_full(lp):
            entries.append(("Expression", nm.advice_for_number(expr, area)))
        if (nm.reduce_full(soul) != nm.reduce_full(lp)
                and nm.reduce_full(soul) != nm.reduce_full(expr)):
            entries.append(("Soul Urge", nm.advice_for_number(soul, area)))
        report["areas"].append((area_titles[area], entries))

    # Karmic debts
    kd_meanings = {
        13: "13/4: Learn discipline, work, and honesty. Cutting corners will backfire.",
        14: "14/5: Learn moderation and freedom within limits. Addiction and escapism are the traps.",
        16: "16/7: Learn humility and inner truth. Ego collapse is the lesson.",
        19: "19/1: Learn independence and leadership without domination. You may have to stand alone.",
    }
    for label, val in kd:
        report["karmic_debts"].append((label, val, kd_meanings.get(val, "")))

    # Karmic lessons
    lessons = {
        1: "You must learn to stand alone and assert yourself.",
        2: "You must learn patience, partnership, and sensitivity.",
        3: "You must learn to express yourself and allow joy.",
        4: "You must learn discipline, order, and follow-through.",
        5: "You must learn adaptability, freedom, and moderation.",
        6: "You must learn responsibility, love, and service.",
        7: "You must learn introspection, truth, and faith.",
        8: "You must learn to handle money, power, and authority.",
        9: "You must learn compassion, forgiveness, and letting go.",
    }
    for n in kl:
        report["karmic_lessons"].append((n, lessons[n]))

    # Hidden passion / subconscious
    for n in hp:
        report["hidden_passion"].append((n, nm.NUMEROLOGY_DESCRIPTIONS.get(n, "")[:150]))
    report["subconscious"] = f"{ss}/9"

    # Pinnacles
    for num, period in pins:
        report["pinnacles"].append((period, num, nm.NUMEROLOGY_DESCRIPTIONS.get(num, "")[:120]))

    # Challenges
    challenge_desc = {
        0: "The challenge of choice — you must learn to make decisions and trust yourself.",
        1: "The challenge of independence — you must learn to stand alone and assert yourself.",
        2: "The challenge of sensitivity — you must learn to be patient and not take things personally.",
        3: "The challenge of expression — you must learn to communicate and not scatter your energy.",
        4: "The challenge of discipline — you must learn order, work, and follow-through.",
        5: "The challenge of freedom — you must learn moderation and not run from commitment.",
        6: "The challenge of responsibility — you must learn to serve without martyring yourself.",
        7: "The challenge of truth — you must learn to trust and not isolate.",
        8: "The challenge of power — you must learn to handle money and authority with integrity.",
        9: "The challenge of compassion — you must learn to let go and forgive.",
    }
    for i, c in enumerate(chals, 1):
        report["challenges"].append((i, c, challenge_desc.get(c, "")))

    # Cycles
    for label, c in [("Formative cycle (youth)", cycles[0]),
                     ("Productive cycle (middle age)", cycles[1]),
                     ("Harvest cycle (maturity)", cycles[2])]:
        report["cycles"].append((label, c, nm.NUMEROLOGY_DESCRIPTIONS.get(c, "")[:150]))

    # Personal year
    py_meanings = {
        1: "A year of new beginnings, independence, and planting seeds.",
        2: "A year of patience, partnership, and waiting for seeds to grow.",
        3: "A year of expression, creativity, and social expansion.",
        4: "A year of work, discipline, and building foundations.",
        5: "A year of change, freedom, and unexpected opportunities.",
        6: "A year of responsibility, family, and service.",
        7: "A year of introspection, learning, and spiritual growth.",
        8: "A year of power, money, and achievement.",
        9: "A year of endings, release, and preparing for renewal.",
    }
    report["personal_year"] = (py, py_meanings.get(py, ""))

    # Blunt truth
    core_challenge = lp if lp not in nm.MASTER_NUMBERS else nm.reduce_full(lp)
    shadow_raw = nm.ASPECTS.get(core_challenge, nm.ASPECTS[1])["shadow"].rstrip()
    if not shadow_raw.endswith("."):
        shadow_raw += "."
    report["blunt"] = {
        "challenge": shadow_raw[0].upper() + shadow_raw[1:],
        "advice": nm.ASPECTS.get(core_challenge, nm.ASPECTS[1])["advice"],
    }
    return report


def pdf_bytes_from_report(report: dict) -> bytes:
    """Build the PDF in memory and return raw bytes for st.download_button."""
    buf = io.BytesIO()
    nm.generate_pdf_report(report, output_path=buf)
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------
st.markdown('<div class="main-title">🔮 Detailed Numerology Analyzer</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Enter your full birth name and birth date to generate '
    'an in-depth numerology report with a downloadable PDF.</div>',
    unsafe_allow_html=True,
)

with st.form("input_form"):
    name = st.text_input(
        "Full Birth Name (as on birth certificate)",
        placeholder="e.g. Souparna Paul",
    )
    dob = st.text_input(
        "Birth Date (MMDDYYYY)",
        placeholder="e.g. 11212000",
    )
    submitted = st.form_submit_button("✨ Generate Report", use_container_width=True)


if submitted:
    # --- Validate ---
    errors = []
    if not name or not any(c.isalpha() for c in name):
        errors.append("Please enter a valid name with letters.")
    if len(dob) != 8 or not dob.isdigit():
        errors.append("Birth date must be 8 digits in MMDDYYYY format.")
    else:
        try:
            datetime.datetime.strptime(dob, "%m%d%Y")
        except ValueError:
            errors.append("That is not a real calendar date.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Crunching the numbers..."):
            report = build_report_dict(name, dob)
            pdf_bytes = pdf_bytes_from_report(report)

        st.success("Report generated!")

        # ---- Download button ----
        safe = "".join(c if c.isalnum() else "_" for c in name)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"numerology_report_{safe}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        # ---- On-screen report ----
        st.markdown("---")
        st.markdown(f"### Report for **{report['name']}**  ·  {report['dob']}")

        # Part 1
        st.markdown('<div class="section-head">PART 1 — Core Numbers</div>',
                    unsafe_allow_html=True)
        for title, number, desc, extra in report["core"]:
            st.markdown(f'<div class="num-head">{title}: {number}</div>',
                        unsafe_allow_html=True)
            st.write(desc)
            for line in extra or []:
                st.caption(line)

        # Part 2
        if report["synthesis"]:
            st.markdown('<div class="section-head">PART 2 — Dynamic Synthesis</div>',
                        unsafe_allow_html=True)
            for i, s in enumerate(report["synthesis"], 1):
                st.write(f"**{i}.** {s}")

        # Part 3
        if report["areas"]:
            st.markdown('<div class="section-head">PART 3 — Life Area Analysis & Advice</div>',
                        unsafe_allow_html=True)
            for area_title, entries in report["areas"]:
                st.markdown(f"**{area_title}**")
                for source, text in entries:
                    st.write(f"**{source}:** {text}")
                st.write("")

        # Part 4
        if report["karmic_debts"] or report["karmic_lessons"]:
            st.markdown('<div class="section-head">PART 4 — Karmic Patterns</div>',
                        unsafe_allow_html=True)
            if report["karmic_debts"]:
                st.markdown("**Karmic Debts**")
                for label, value, meaning in report["karmic_debts"]:
                    st.write(f"- **{label}** ({value}): {meaning}")
            if report["karmic_lessons"]:
                st.markdown("**Karmic Lessons (missing numbers)**")
                for n, meaning in report["karmic_lessons"]:
                    st.write(f"- **Missing {n}:** {meaning}")

        # Part 5
        if report["hidden_passion"] or report["subconscious"]:
            st.markdown('<div class="section-head">PART 5 — Hidden Passion & Subconscious Self</div>',
                        unsafe_allow_html=True)
            if report["hidden_passion"]:
                st.markdown("**Hidden Passion**")
                for n, text in report["hidden_passion"]:
                    st.write(f"- **{n}:** {text}")
            if report["subconscious"]:
                st.write(f"**Subconscious Self:** {report['subconscious']}")

        # Part 6
        if report["planes"]:
            st.markdown('<div class="section-head">PART 6 — Planes of Expression</div>',
                        unsafe_allow_html=True)
            st.table([{"Plane": k, "Count": v} for k, v in report["planes"].items()])

        # Part 7
        if report["pinnacles"] or report["challenges"]:
            st.markdown('<div class="section-head">PART 7 — Pinnacles & Challenges</div>',
                        unsafe_allow_html=True)
            if report["pinnacles"]:
                st.markdown("**Pinnacles (peak opportunities)**")
                for period, number, text in report["pinnacles"]:
                    st.write(f"- **{period}:** {number} — {text}")
            if report["challenges"]:
                st.markdown("**Challenges (lessons to overcome)**")
                for idx, number, meaning in report["challenges"]:
                    st.write(f"- **Challenge {idx}:** {number} — {meaning}")

        # Part 8
        if report["cycles"]:
            st.markdown('<div class="section-head">PART 8 — Life Cycles</div>',
                        unsafe_allow_html=True)
            for label, number, text in report["cycles"]:
                st.markdown(f"**{label}: {number}**")
                st.write(text)

        # Part 9
        if report["personal_year"]:
            py, meaning = report["personal_year"]
            st.markdown('<div class="section-head">PART 9 — Personal Year</div>',
                        unsafe_allow_html=True)
            st.write(f"**Personal Year {py}:** {meaning}")

        # Part 10
        if report["blunt"]:
            st.markdown('<div class="section-head">PART 10 — The Blunt Truth</div>',
                        unsafe_allow_html=True)
            st.write(report["blunt"]["challenge"])
            st.info(report["blunt"]["advice"])

        # Disclaimer
        st.markdown(f'<div class="disclaimer">{report["disclaimer"]}</div>',
                    unsafe_allow_html=True)
elif __name__ == "__main__" and not st.runtime.exists():
    # Fallback: running as plain python (not via `streamlit run`)
    print("Tip: run with `streamlit run streamlit_app.py` for the web UI.")
    print("Falling back to CLI mode...\n")
    import numerology as _nm
    _cli_name = input("Enter your FULL BIRTH NAME: ").strip()
    _cli_dob = input("Enter your BIRTH DATE (MMDDYYYY): ").strip()
    _safe = "".join(c if c.isalnum() else "_" for c in _cli_name)
    _nm.generate_report(_cli_name, _cli_dob,
                        pdf_path=f"numerology_report_{_safe}.pdf")

else:
    with st.sidebar:
        st.markdown("### About")
        st.write(
            "This tool computes Pythagorean numerology from your full birth "
            "name and birth date. It produces a long, blunt, archetypal report "
            "covering career, money, love, health, spirituality, and shadow work."
        )
        st.markdown("### Requirements")
        st.write("- Python 3.8+")
        st.write("- `reportlab`")
        st.write("- `streamlit`")
        st.markdown("### Disclaimer")
        st.caption(
            "For reflection and entertainment only. Not a substitute for "
            "professional advice."
        )