import datetime
import io
import os
from itertools import combinations

# --- PDF export (reportlab) ---
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)

# --- Numerology Mappings ---

LETTER_VALUES = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}

VOWELS = set("AEIOU")
# In numerology, Y is treated as a vowel when it sounds like one.
# We use a heuristic: Y is a vowel if it's not adjacent to another vowel
# and is at the end of a syllable-like position. For simplicity here,
# Y is treated as a vowel only when it follows a consonant and is not
# the first letter — plus the common "Y as vowel" cases.

MASTER_NUMBERS = {11, 22, 33}

# --- Descriptions (base personalities) ---

NUMEROLOGY_DESCRIPTIONS = {
    1: "The Leader — Independent, ambitious, pioneering. You are wired to originate, not follow. Your instinct is to take charge, and you resent being managed. The shadow side: arrogance, impatience, and a fear of vulnerability that masquerades as strength.",
    2: "The Peacemaker — Cooperative, diplomatic, sensitive. You read rooms and emotions effortlessly. You thrive in partnership and hate conflict. The shadow side: people-pleasing, indecision, and suppressing your own needs until you resent everyone around you.",
    3: "The Communicator — Creative, expressive, joyful. You have a gift for words, art, or performance. You light up rooms. The shadow side: scattering your energy, avoiding depth, using charm to dodge responsibility, and moodiness you hide behind humor.",
    4: 'The Builder — Practical, disciplined, stable. You are the foundation others stand on. You value order and follow-through. The shadow side: rigidity, workaholism, resistance to change, and using "being busy" as an excuse to avoid feeling.',
    5: "The Freethinker — Adventurous, adaptable, curious. You crave freedom, novelty, and experience. You are versatile and quick. The shadow side: impulsiveness, commitment-phobia, addiction to stimulation, and running from problems by changing scenery.",
    6: "The Nurturer — Responsible, compassionate, artistic. You are drawn to family, service, and beauty. You are the one everyone leans on. The shadow side: martyrdom, control disguised as care, and losing yourself in others' problems.",
    7: "The Seeker — Analytical, spiritual, introspective. You need solitude and truth. You see through surfaces. The shadow side: emotional detachment, cynicism, isolation, and using intellect to avoid intimacy.",
    8: "The Executive — Ambitious, powerful, prosperous. You are built for the material world — money, authority, scale. The shadow side: workaholism, control, defining yourself by status, and crushing softness in yourself and others.",
    9: "The Humanitarian — Compassionate, generous, idealistic. You feel the world's pain and want to heal it. The shadow side: martyrdom, boundary issues, rescuing people who don't want saving, and bitterness when the world doesn't reciprocate.",
    11: 'The Master Intuitive — (Master Number) Highly intuitive, visionary, inspiring. You are a channel for insight and can lift others. The shadow side: anxiety, nervous exhaustion, feeling "too much," and escaping into fantasy instead of grounding your vision.',
    22: "The Master Builder — (Master Number) Powerful, ambitious, practical visionary. You can turn grand dreams into concrete reality at scale. The shadow side: paralysis by the size of your vision, and self-sabotage when you feel unworthy of your own potential.",
    33: "The Master Healer/Teacher — (Master Number) Unconditional love, compassion, healing on a universal level. Very rare and demanding. The shadow side: carrying others' burdens until you collapse, and confusing self-sacrifice with love."
}

# --- Detailed aspect banks per number ---

ASPECTS = {
    1: {
        "career": "You need autonomy. Working under a micromanager will make you sick. Best in entrepreneurship, leadership, or any role where you set the direction. You will stagnate in a job with no upward path.",
        "money": "You earn well when you bet on yourself. You are bad at saving and worse at asking for help. Your financial risk is ego-driven spending and refusing to negotiate.",
        "love": "You need a partner who respects your independence and doesn't compete with you. You struggle to say 'I need you.' You confuse being needed with being loved.",
        "health": "Stress hits your head, blood pressure, and sleep. You push through exhaustion until you crash. You must learn to rest before you break.",
        "spirituality": "Your path is will and courage. You grow by acting despite fear, not by waiting for certainty.",
        "shadow": "Arrogance, impatience, fear of dependency, and a deep terror of being seen as weak.",
        "advice": "Pick one thing and finish it. Ask for help this week — out loud. Let someone else lead once and notice you didn't die. Your independence is a strength; your refusal to lean on anyone is a wound."
    },
    2: {
        "career": "You excel in partnerships, diplomacy, counseling, HR, mediation, and support roles. You are the glue. But you will be overlooked if you never claim credit. Learn to say 'I did that.'",
        "money": "You are cautious, sometimes to a fault. You undercharge. You may let a partner control finances. Your risk is financial dependence, not recklessness.",
        "love": "You are a devoted partner. You sense your partner's mood before they speak. The danger: losing yourself, tolerating too much, and calling it loyalty.",
        "health": "Stress hits your stomach, immune system, and nerves. You absorb others' emotions physically. You need solitude to recover, even though you crave company.",
        "spirituality": "Your path is love, patience, and boundaries. You grow by learning that 'no' is not a betrayal.",
        "shadow": "People-pleasing, resentment, passive aggression, and chronic indecision.",
        "advice": "State one need today without softening it. Practice saying no without an excuse. Your sensitivity is a gift, but unguarded it becomes a doorway for others to walk all over you."
    },
    3: {
        "career": "You shine in creative fields, communication, teaching, sales, entertainment, writing. You need variety. Repetitive work kills you. You must finish what you start or you'll be known as 'almost.'",
        "money": "Money comes in waves. You spend on fun, beauty, and experiences. You avoid looking at your accounts. Your risk is denial and lack of structure.",
        "love": "You are fun, warm, and expressive. You need a partner who lets you shine and doesn't demand you dim. You flee from heaviness. You must learn to stay when it's not fun.",
        "health": "Stress hits your throat, skin, and mood. You are prone to scattered energy and burnout from over-socializing. You need creative outlets or you get depressed.",
        "spirituality": "Your path is joy, expression, and truth. You grow by saying the hard thing, not just the pretty thing.",
        "shadow": "Scattering, avoidance, superficiality, and using charm to dodge accountability.",
        "advice": "Finish the thing you started. Sit with one hard emotion for ten minutes without joking. Your voice is your power — use it for truth, not just applause."
    },
    4: {
        "career": "You are the backbone of any organization: operations, finance, engineering, construction, law, project management. You are trusted. You can get stuck in a job that's stable but deadening.",
        "money": "You are disciplined and good at saving. You may be too conservative and miss growth. Your risk is fear-based hoarding and refusing to invest in yourself.",
        "love": "You are loyal and dependable. You show love through acts of service. You struggle to express emotion verbally. Your partner may feel loved but not *seen*.",
        "health": "Stress hits your back, joints, and digestion. You carry tension. You need routine and rest, but you often work through pain.",
        "spirituality": "Your path is discipline, patience, and faith. You grow by trusting what you can't control.",
        "shadow": "Rigidity, workaholism, emotional avoidance, and resistance to change.",
        "advice": "Change one routine this week on purpose. Say 'I love you' out loud without a task attached. Your stability is a gift — but a foundation that never moves becomes a tomb."
    },
    5: {
        "career": "You need freedom, travel, variety, and novelty. Best in sales, media, travel, entrepreneurship, or any role with change. You will suffocate in a cubicle with a strict schedule.",
        "money": "Money flows in and out. You are good at earning, poor at keeping. Your risk is impulsive spending and no safety net. Automate savings or you'll have none.",
        "love": "You need a partner who gives you space and doesn't confuse freedom with betrayal. You are exciting but hard to pin down. You must learn that commitment is not a cage.",
        "health": "Stress hits your nervous system, sleep, and adrenaline. You burn the candle at both ends. You need movement, but also real rest — not just a new distraction.",
        "spirituality": "Your path is freedom, experience, and presence. You grow by staying still long enough to hear yourself.",
        "shadow": "Impulsiveness, commitment-phobia, escapism, and addiction to stimulation.",
        "advice": "Stay in one place long enough to feel the discomfort. Finish one commitment before starting the next. Freedom is not the absence of limits — it's the ability to choose your limits."
    },
    6: {
        "career": "You thrive in service, healing, teaching, counseling, design, hospitality, and family-oriented work. You are the one who holds the team together. You may over-give and be taken for granted.",
        "money": "You spend on family, home, and beauty. You may bail others out financially. Your risk is over-extending and being the family bank.",
        "love": "You are devoted, romantic, and nurturing. You may mother your partner. You must learn to receive, not just give. You attract people who need fixing.",
        "health": "Stress hits your heart, chest, and weight. You carry others' burdens. You need to put your own oxygen mask on first.",
        "spirituality": "Your path is love, service, and boundaries. You grow by realizing that sacrificing yourself is not the same as loving.",
        "shadow": "Martyrdom, control disguised as care, and resentment from over-giving.",
        "advice": "Let someone take care of you this week without managing how they do it. Say no to one request that drains you. Your love is medicine — but you are not a pharmacy."
    },
    7: {
        "career": "You need depth, analysis, and solitude. Best in research, science, tech, philosophy, writing, spirituality, or investigation. You hate being managed and dislike surface-level work.",
        "money": "You are not motivated by money, which means you often under-earn. You need a practical system because you won't track it naturally. Your risk is ignoring finances until they become a crisis.",
        "love": "You need a partner who respects your solitude and doesn't take it personally. You struggle to express emotion. You may choose isolation over vulnerability and call it peace.",
        "health": "Stress hits your mind, sleep, and nervous system. You overthink into insomnia. You need silence, nature, and time alone to recharge.",
        "spirituality": "Your path is truth, wisdom, and inner knowing. You grow by trusting your intuition over your analysis sometimes.",
        "shadow": "Emotional detachment, cynicism, isolation, and intellectual arrogance.",
        "advice": "Tell one person one true feeling this week without analyzing it. Let someone in. Your mind is a fortress — but a fortress with no door is a prison."
    },
    8: {
        "career": "You are built for leadership, business, finance, law, real estate, and large-scale ventures. You can handle power and money. You may sacrifice health and family for status.",
        "money": "You are good with money and can attract it. Your risk is defining yourself by your net worth and crashing when it fluctuates. You must learn that you are not your bank account.",
        "love": "You are protective and generous, but you can be controlling and emotionally unavailable. You show love by providing. You must learn to be present, not just powerful.",
        "health": "Stress hits your heart, blood pressure, and back. You work too much. You must schedule rest like a meeting or you won't take it.",
        "spirituality": "Your path is power, balance, and integrity. You grow by using power in service of something bigger than yourself.",
        "shadow": "Workaholism, control, status-seeking, and crushing softness in yourself and others.",
        "advice": "Tell someone you love them without also solving a problem for them. Take one full day off and don't check your phone. Your power is real — but power without tenderness becomes tyranny."
    },
    9: {
        "career": "You thrive in humanitarian, artistic, healing, and service-oriented work. You need meaning. You will burn out in a soulless job. You may give too much and resent it.",
        "money": "You are generous, sometimes to your own detriment. You may give away money you need. Your risk is martyrdom and financial instability from over-giving.",
        "love": "You love deeply and universally. You may attract people who need rescuing. You must learn that you cannot save everyone and that loving someone doesn't mean fixing them.",
        "health": "Stress hits your immune system, heart, and energy. You absorb the world's pain. You need to protect your energy and rest without guilt.",
        "spirituality": "Your path is compassion, surrender, and universal love. You grow by letting go of what you cannot control.",
        "shadow": "Martyrdom, boundary issues, rescuing, and bitterness when the world doesn't reciprocate.",
        "advice": "Let one person solve their own problem without your help. Give to yourself first this week. Your compassion is a gift — but you are not the world's savior, and pretending you are is not humility; it's ego in disguise."
    },
    11: {
        "career": "You are a visionary, teacher, artist, healer, or spiritual guide. You need work that inspires. You may struggle with anxiety and self-doubt that blocks your potential.",
        "money": "You may undervalue your gifts and undercharge. You need practical grounding. Your risk is financial instability from idealism and avoidance.",
        "love": "You need a partner who sees your depth and doesn't dismiss your sensitivity. You may attract people who don't understand you. You must learn to communicate your inner world.",
        "health": "Stress hits your nervous system, sleep, and mental health. You are highly sensitive. You need grounding, nature, and nervous-system regulation.",
        "spirituality": "Your path is intuition, inspiration, and service. You grow by trusting your inner voice and grounding your visions in reality.",
        "shadow": "Anxiety, nervous exhaustion, escapism, and feeling 'too much' for the world.",
        "advice": "Ground your vision in one concrete action today. Your sensitivity is not a weakness — but ungrounded, it becomes chaos. You are here to inspire, not to be understood by everyone."
    },
    22: {
        "career": "You are a master builder. You can create large-scale, lasting structures. You need big challenges. You may self-sabotage by shrinking or procrastinating because the vision feels too big.",
        "money": "You have the potential for great wealth and great impact. Your risk is paralysis and fear of your own power. You must start small and build.",
        "love": "You need a partner who supports your vision and doesn't compete with it. You may prioritize work over love. You must learn that intimacy is also a building project.",
        "health": "Stress hits your back, heart, and nervous system. You carry the weight of your vision. You must rest or you will break.",
        "spirituality": "Your path is manifesting spirit into matter. You grow by trusting that you are worthy of your own potential.",
        "shadow": "Paralysis, self-sabotage, and feeling unworthy of your own potential.",
        "advice": "Break your big dream into one step you can take today. Stop waiting to feel ready. The world needs what you can build — but you must start."
    },
    33: {
        "career": "You are a healer and teacher. You are drawn to service on a universal level. You may carry others' burdens until you collapse. You need boundaries or you will burn out.",
        "money": "You may give away too much. You need to balance service with self-care. Your risk is financial martyrdom.",
        "love": "You love unconditionally, sometimes to your own detriment. You must learn that love doesn't mean self-erasure.",
        "health": "Stress hits your heart, immune system, and energy. You absorb everything. You need deep rest and energetic boundaries.",
        "spirituality": "Your path is unconditional love, healing, and teaching. You grow by realizing that you cannot pour from an empty cup.",
        "shadow": "Martyrdom, self-sacrifice, and confusing self-erasure with love.",
        "advice": "You are not here to save everyone. Let someone carry their own weight this week. Your love is powerful — but you must include yourself in it."
    }
}

# --- Helper functions ---

def reduce_number(num, allow_master=True):
    """Reduce to a single digit, preserving master numbers if allowed."""
    num = int(num)
    while num > 9:
        if allow_master and num in MASTER_NUMBERS:
            return num
        num = sum(int(d) for d in str(num))
    return num

def reduce_full(num):
    """Reduce to a single digit, ignoring master numbers (for karmic/cycle work)."""
    num = int(num)
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num

# --- PDF Helpers ----------------------------------------------------------

PDF_STYLES = None

def _pdf_styles():
    """Build and cache ParagraphStyles for the report."""
    global PDF_STYLES
    if PDF_STYLES is not None:
        return PDF_STYLES

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontSize=22, leading=26,
            alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontSize=11, leading=14,
            alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontSize=15, leading=19,
            textColor=colors.HexColor("#16213e"), spaceBefore=14, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=12.5, leading=16,
            textColor=colors.HexColor("#0f3460"), spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontSize=10, leading=14,
            alignment=TA_LEFT, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["BodyText"], fontSize=10, leading=14,
            leftIndent=16, bulletIndent=6, spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "quote", parent=base["BodyText"], fontSize=10, leading=14,
            leftIndent=14, rightIndent=14, textColor=colors.HexColor("#333333"),
            borderColor=colors.HexColor("#cccccc"), borderWidth=0.5,
            borderPadding=6, spaceAfter=8,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontSize=8.5, leading=11,
            textColor=colors.HexColor("#777777"),
        ),
    }
    PDF_STYLES = styles
    return styles


import re

# Tags we want reportlab to actually interpret (NOT escape).
# Matches: <b>, </b>, <i>, <br/>, <br>, <font color="...">, etc.
_ALLOWED_TAGS = re.compile(
    r"(</?(?:b|i|u|br|font|para|super|sub)(?:\s+[^>]*)?/?>)",
    re.IGNORECASE
)


def _esc(text):
    """
    Escape XML-sensitive characters for reportlab Paragraph,
    but preserve a whitelist of inline formatting tags so <b>...</b>
    renders as bold instead of literal text.
    """
    if text is None:
        return ""

    text = str(text)

    # re.split with a capturing group returns a list where some elements
    # may be None (when the split produces an empty leading/trailing chunk).
    parts = _ALLOWED_TAGS.split(text)

    out = []
    for i, chunk in enumerate(parts):
        if chunk is None:
            continue
        if i % 2 == 1:
            # this is a captured tag — keep as-is
            out.append(chunk)
        else:
            # ordinary text — escape XML-sensitive characters
            out.append(
                chunk.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
            )
    return "".join(out)


def _para(text, style):
    return Paragraph(_esc(text), style)


def _hr(color="#cccccc", thickness=0.6, space_before=8, space_after=8):
    """
    Horizontal rule rendered as a 1-row Table with a bottom border.
    Avoids HRFlowable's dash artifact that some PDF text extractors
    read as a flood of '1' characters.
    """
    t = Table([[""]], colWidths=["100%"], rowHeights=[0.1])
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), thickness, colors.HexColor(color)),
        ("TOPPADDING", (0, 0), (-1, -1), space_before),
        ("BOTTOMPADDING", (0, 0), (-1, -1), space_after),
    ]))
    return t


def _section_header(text, styles, first=False):
    """Standard section header: optional rule, heading, rule."""
    flow = []
    if not first:
        flow.append(Spacer(1, 6))
    flow.append(_para(text, styles["h1"]))
    flow.append(_hr("#0f3460", 0.8, space_before=2, space_after=8))
    return flow


def _footer(canvas, doc):
    """Draw page number footer."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawCentredString(
        LETTER[0] / 2.0, 0.5 * inch,
        f"Numerology Report  —  page {doc.page}"
    )
    canvas.restoreState()


def generate_pdf_report(report_data, output_path=None):
    """
    Build a PDF from a structured report dict.

    report_data expected keys (all optional except name/dob):
      name, dob,
      core (list of (title, number, description, extra_lines)),
      synthesis (list of strings),
      areas (list of (area_title, list of (source, text))),
      karmic_debts (list of (label, value, meaning)),
      karmic_lessons (list of (number, meaning)),
      hidden_passion (list of (number, text)),
      subconscious (str),
      planes (dict),
      pinnacles (list of (period, number, text)),
      challenges (list of (index, number, meaning)),
      cycles (list of (label, number, text)),
      personal_year (tuple (py, meaning)),
      blunt (dict with challenge + advice),
      disclaimer (str),
    """
    if output_path is None:
        safe = "".join(c if c.isalnum() else "_" for c in report_data.get("name", "report"))
        output_path = f"numerology_report_{safe}.pdf"

    styles = _pdf_styles()
    doc = SimpleDocTemplate(
        output_path, pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        title="Numerology Report", author="Numerology Analyzer",
    )
    story = []

    # Cover
    story.append(Spacer(1, 0.4 * inch))
    story.append(_para("DETAILED NUMEROLOGY ANALYSIS", styles["title"]))
    story.append(_para(report_data.get("name", ""), styles["subtitle"]))
    story.append(_para(f"Birth Date: {report_data.get('dob', '')}", styles["subtitle"]))
    story.append(_hr("#1a1a2e", 1.2, space_before=10, space_after=14))
    story.append(Spacer(1, 0.1 * inch))

    # Core numbers
    story.extend(_section_header("PART 1 — CORE NUMBERS", styles, first=True))
    for title, number, desc, extra in report_data.get("core", []):
        story.append(_para(f"<b>{title}: {number}</b>", styles["h2"]))
        story.append(_para(desc, styles["body"]))
        for line in extra or []:
            story.append(_para(f"<i>{line}</i>", styles["small"]))
    story.append(_hr())

    # Synthesis
    syn = report_data.get("synthesis", [])
    if syn:
        story.append(_para("PART 2 — DYNAMIC SYNTHESIS", styles["h1"]))
        for i, s in enumerate(syn, 1):
            story.append(_para(f"{i}. {s}", styles["body"]))
        story.append(_hr())

    # Life areas
    areas = report_data.get("areas", [])
    if areas:
        story.append(_para("PART 3 — LIFE AREA ANALYSIS & ADVICE", styles["h1"]))
        for area_title, entries in areas:
            story.append(_para(f"<b>{area_title}</b>", styles["h2"]))
            for source, text in entries:
                story.append(_para(f"<b>{source}:</b> {text}", styles["body"]))
            story.append(Spacer(1, 4))
        story.append(_hr())

    # Karmic
    kd = report_data.get("karmic_debts", [])
    kl = report_data.get("karmic_lessons", [])
    if kd or kl:
        story.append(_para("PART 4 — KARMIC PATTERNS", styles["h1"]))
        if kd:
            story.append(_para("<b>Karmic Debts</b>", styles["h2"]))
            for label, value, meaning in kd:
                story.append(Paragraph(
                    _esc(f"<b>{label}</b> ({value}): {meaning}"),
                    styles["bullet"], bulletText="•"
                ))
        if kl:
            story.append(_para("<b>Karmic Lessons (missing numbers)</b>", styles["h2"]))
            for n, meaning in kl:
                story.append(Paragraph(
                    _esc(f"<b>Missing {n}:</b> {meaning}"),
                    styles["bullet"], bulletText="•"
                ))
        story.append(_hr())

    # Hidden passion / subconscious
    hp = report_data.get("hidden_passion", [])
    sub = report_data.get("subconscious")
    if hp or sub:
        story.append(_para("PART 5 — HIDDEN PASSION & SUBCONSCIOUS SELF", styles["h1"]))
        if hp:
            story.append(_para("<b>Hidden Passion</b>", styles["h2"]))
            for n, text in hp:
                story.append(Paragraph(
                    _esc(f"<b>{n}:</b> {text}"),
                    styles["bullet"], bulletText="•"
                ))
        if sub:
            story.append(_para(f"Subconscious Self: {sub}", styles["body"]))
        story.append(_hr())

    # Planes
    planes = report_data.get("planes")
    if planes:
        story.append(_para("PART 6 — PLANES OF EXPRESSION", styles["h1"]))
        header = [_para("<b>Plane</b>", styles["body"]),
                  _para("<b>Count</b>", styles["body"])]
        rows = [header]
        for k, v in planes.items():
            rows.append([_para(k, styles["body"]),
                         _para(str(v), styles["body"])])
        t = Table(rows, colWidths=[3 * inch, 1.2 * inch], hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f4f4f8")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(_hr())

    # Pinnacles & challenges
    pins = report_data.get("pinnacles", [])
    chals = report_data.get("challenges", [])
    if pins or chals:
        story.append(_para("PART 7 — PINNACLES & CHALLENGES", styles["h1"]))
        if pins:
            story.append(_para("<b>Pinnacles (peak opportunities)</b>", styles["h2"]))
            for period, number, text in pins:
                story.append(Paragraph(
                    _esc(f"<b>{period}:</b> {number} — {text}"),
                    styles["bullet"], bulletText="•"
                ))
        if chals:
            story.append(_para("<b>Challenges (lessons to overcome)</b>", styles["h2"]))
            for idx, number, meaning in chals:
                story.append(Paragraph(
                    _esc(f"<b>Challenge {idx}:</b> {number} — {meaning}"),
                    styles["bullet"], bulletText="•"
                ))
        story.append(_hr())

    # Life cycles
    cycles = report_data.get("cycles", [])
    if cycles:
        story.append(_para("PART 8 — LIFE CYCLES", styles["h1"]))
        for label, number, text in cycles:
            story.append(_para(f"{label}: {number}", styles["h2"]))
            story.append(_para(text, styles["body"]))
        story.append(_hr())

    # Personal year
    py = report_data.get("personal_year")
    if py:
        story.append(_para("PART 9 — PERSONAL YEAR", styles["h1"]))
        story.append(_para(f"Personal Year {py[0]}: {py[1]}", styles["body"]))
        story.append(_hr())

    # Blunt truth
    blunt = report_data.get("blunt")
    if blunt:
        story.append(_para("PART 10 — THE BLUNT TRUTH", styles["h1"]))
        story.append(_para(blunt.get("challenge", ""), styles["body"]))
        story.append(_para(blunt.get("advice", ""), styles["quote"]))
        story.append(_hr())

    # Disclaimer
    story.append(_para(report_data.get("disclaimer", ""), styles["small"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return os.path.abspath(output_path)


def is_vowel(char, prev_char, next_char):
    """Heuristic for Y as vowel."""
    if char in VOWELS:
        return True
    if char == 'Y':
        # Y is a vowel when it sounds like one — usually not at start of syllable
        # Heuristic: treat Y as vowel if surrounded by consonants or at end of name
        if prev_char and prev_char not in VOWELS and prev_char.isalpha():
            return True
        if next_char is None or not next_char.isalpha():
            return True
    return False

def letter_sum(name, mode="all"):
    total = 0
    name = name.upper()
    for i, ch in enumerate(name):
        if not ch.isalpha():
            continue
        prev_ch = name[i-1] if i > 0 else None
        next_ch = name[i+1] if i < len(name)-1 else None
        if mode == "all":
            total += LETTER_VALUES.get(ch, 0)
        elif mode == "vowels":
            if is_vowel(ch, prev_ch, next_ch):
                total += LETTER_VALUES.get(ch, 0)
        elif mode == "consonants":
            if not is_vowel(ch, prev_ch, next_ch):
                total += LETTER_VALUES.get(ch, 0)
    return total

# --- Core number calculations ---

def life_path(birth_date_str):
    m, d, y = int(birth_date_str[0:2]), int(birth_date_str[2:4]), int(birth_date_str[4:8])
    m_r = reduce_number(m)
    d_r = reduce_number(d)
    y_r = reduce_number(y)
    total = m_r + d_r + y_r
    lp = reduce_number(total)
    return lp, m_r, d_r, y_r, total

def birth_day_number(birth_date_str):
    d = int(birth_date_str[2:4])
    return reduce_number(d)

def expression_number(name):
    total = letter_sum(name, "all")
    return reduce_number(total), total

def soul_urge_number(name):
    total = letter_sum(name, "vowels")
    return reduce_number(total), total

def personality_number(name):
    total = letter_sum(name, "consonants")
    return reduce_number(total), total

def maturity_number(lp, expr):
    return reduce_number(reduce_number(lp) + reduce_number(expr))

def balance_number(name):
    """Balance number = first letters of each name."""
    parts = [p for p in name.upper().split() if p and p[0].isalpha()]
    total = sum(LETTER_VALUES.get(p[0], 0) for p in parts)
    return reduce_number(total)

def karmic_debts(birth_date_str, name):
    """Karmic debt numbers: 13, 14, 16, 19 in raw sums."""
    debts = []
    m, d, y = int(birth_date_str[0:2]), int(birth_date_str[2:4]), int(birth_date_str[4:8])
    raw_lp = reduce_full(m) + reduce_full(d) + reduce_full(y)
    # Check raw components and totals for 13/14/16/19
    for label, val in [("Life Path raw sum", raw_lp),
                       ("Birth day", d),
                       ("Year", y)]:
        if val in (13, 14, 16, 19):
            debts.append((label, val))
    # Check name raw sums
    for label, raw in [("Expression", letter_sum(name, "all")),
                       ("Soul Urge", letter_sum(name, "vowels")),
                       ("Personality", letter_sum(name, "consonants"))]:
        if raw in (13, 14, 16, 19):
            debts.append((label, raw))
    return debts

def karmic_lessons(name):
    """Missing numbers 1-9 in the name (karmic lessons)."""
    present = set()
    for ch in name.upper():
        if ch.isalpha():
            present.add(LETTER_VALUES.get(ch, 0))
    return sorted(set(range(1, 10)) - present)

def hidden_passion(name):
    """Most frequent letter values in the name."""
    counts = {}
    for ch in name.upper():
        if ch.isalpha():
            v = LETTER_VALUES.get(ch, 0)
            counts[v] = counts.get(v, 0) + 1
    if not counts:
        return []
    max_count = max(counts.values())
    return sorted([v for v, c in counts.items() if c == max_count])

def subconscious_self(name):
    """Number of letters present (1-9) in the name."""
    present = set()
    for ch in name.upper():
        if ch.isalpha():
            present.add(LETTER_VALUES.get(ch, 0))
    return len(present)

def planes_of_expression(name):
    """Physical (E,I,O,U / body), Mental (A,H,J,N,P,G,L), Emotional (B,C,D,F,K,M,Q,R,S,T,V,W,X,Y,Z)."""
    physical_letters = set("EIOU")
    mental_letters = set("AHJN PGL".replace(" ", ""))
    emotional_letters = set("BCDFKMQRSTVWXYZ")
    counts = {"Physical": 0, "Mental": 0, "Emotional": 0, "Intuitive": 0}
    for ch in name.upper():
        if not ch.isalpha():
            continue
        if ch in physical_letters:
            counts["Physical"] += 1
        elif ch in mental_letters:
            counts["Mental"] += 1
        elif ch in emotional_letters:
            counts["Emotional"] += 1
        else:
            counts["Intuitive"] += 1
    return counts

def pinnacles(birth_date_str):
    """Four Pinnacles using month, day, year."""
    m, d, y = int(birth_date_str[0:2]), int(birth_date_str[2:4]), int(birth_date_str[4:8])
    m, d, y = reduce_full(m), reduce_full(d), reduce_full(y)
    p1 = reduce_number(m + d)
    p2 = reduce_number(d + y)
    p3 = reduce_number(p1 + p2)
    p4 = reduce_number(m + y)
    # Age ranges
    first_end = 36 - reduce_full(int(birth_date_str[0:2]) + int(birth_date_str[2:4]))
    return [(p1, f"Birth to age {first_end}"),
            (p2, f"Age {first_end+1} to {first_end+9}"),
            (p3, f"Age {first_end+10} to {first_end+18}"),
            (p4, f"Age {first_end+19} onward")]

def challenges(birth_date_str):
    """Four Challenges."""
    m, d, y = int(birth_date_str[0:2]), int(birth_date_str[2:4]), int(birth_date_str[4:8])
    m, d, y = reduce_full(m), reduce_full(d), reduce_full(y)
    c1 = abs(m - d)
    c2 = abs(d - y)
    c3 = abs(c1 - c2)
    c4 = abs(m - y)
    return [c1, c2, c3, c4]

def life_cycles(birth_date_str):
    """Three Life Cycles: month, day, year."""
    m, d, y = int(birth_date_str[0:2]), int(birth_date_str[2:4]), int(birth_date_str[4:8])
    return reduce_full(m), reduce_full(d), reduce_full(y)

def personal_year(birth_date_str, current_year=None):
    if current_year is None:
        current_year = datetime.datetime.now().year
    m, d = int(birth_date_str[0:2]), int(birth_date_str[2:4])
    total = reduce_full(m) + reduce_full(d) + reduce_full(current_year)
    return reduce_number(total)

# --- Dynamic synthesis ---

def synthesize(numbers_dict):
    """Cross-reference numbers to produce insights."""
    insights = []
    lp = numbers_dict.get("Life Path")
    expr = numbers_dict.get("Expression")
    soul = numbers_dict.get("Soul Urge")
    pers = numbers_dict.get("Personality")
    bd = numbers_dict.get("Birth Day")
    mat = numbers_dict.get("Maturity")
    bal = numbers_dict.get("Balance")

    def core(n):
        return reduce_full(n) if n not in MASTER_NUMBERS else n

    lp_c, expr_c, soul_c, pers_c = core(lp), core(expr), core(soul), core(pers)

    # 1. Life Path vs Expression
    if lp_c == expr_c:
        insights.append("Your Life Path and Expression are the same. You are not here to explore a different identity — you are here to fully become who you already are. This is a rare alignment: your outer talents match your inner purpose. The risk is monotony and taking yourself for granted.")
    else:
        insights.append(f"Your Life Path ({lp}) and Expression ({expr}) differ. You are here to live one energy while expressing another. This creates inner tension — you may feel like your talents pull you in a direction your soul didn't choose. The work is to let your expression serve your path, not distract from it.")

    # 2. Soul Urge vs Personality
    if soul_c == pers_c:
        insights.append("Your Soul Urge and Personality match. What you want and how you appear are aligned. People see the real you. The risk is that you have nowhere to hide — and you may not have developed a private inner life.")
    else:
        insights.append(f"Your Soul Urge ({soul}) and Personality ({pers}) differ. There is a gap between what you want and how you come across. People may misread you. You may feel unseen. You must learn to communicate your inner world instead of waiting to be discovered.")

    # 3. Life Path vs Soul Urge
    if lp_c == soul_c:
        insights.append("Your Life Path and Soul Urge match. Your deepest desire is exactly what you are here to do. This is a powerful alignment — you want what you need. The risk is obsession and defining yourself entirely by your purpose.")
    else:
        insights.append(f"Your Life Path ({lp}) and Soul Urge ({soul}) differ. What you want deep down is not always what you are here to do. This is the classic 'talent vs desire' tension. You may need to accept that your purpose is not always your passion.")

    # 4. Birth Day number
    insights.append(f"Your Birth Day number is {bd}. This is a special talent you were born with — it colors how you act day to day. {NUMEROLOGY_DESCRIPTIONS.get(bd, '')[:120]}...")

    # 5. Maturity number
    insights.append(f"Your Maturity number is {mat}. This is the energy that unfolds in the second half of life. It is who you are becoming. {NUMEROLOGY_DESCRIPTIONS.get(mat, '')[:120]}...")

    # 6. Balance number
    insights.append(f"Your Balance number is {bal}. When you are stressed, this is the energy you must consciously invoke to regain equilibrium. Work with this number deliberately during hard times.")

    return insights

def advice_for_number(n, area):
    """Return detailed advice for a number in a given life area."""
    bank = ASPECTS.get(n) or ASPECTS.get(reduce_full(n)) or ASPECTS[1]
    return bank.get(area, "No specific guidance available for this number in this area.")

# --- Report generation ---

def generate_report(name, dob, pdf_path=None):
    print("\n" + "=" * 70)
    print(" " * 15 + "DETAILED NUMEROLOGY ANALYSIS")
    print("=" * 70)
    print(f"Name: {name}")
    print(f"Birth Date: {dob[0:2]}/{dob[2:4]}/{dob[4:8]}")
    print("=" * 70)

    # Core numbers
    lp, m_r, d_r, y_r, lp_total = life_path(dob)
    bd = birth_day_number(dob)
    expr, expr_raw = expression_number(name)
    soul, soul_raw = soul_urge_number(name)
    pers, pers_raw = personality_number(name)
    mat = maturity_number(lp, expr)
    bal = balance_number(name)
    kd = karmic_debts(dob, name)
    kl = karmic_lessons(name)
    hp = hidden_passion(name)
    ss = subconscious_self(name)
    planes = planes_of_expression(name)
    pins = pinnacles(dob)
    chals = challenges(dob)
    cycles = life_cycles(dob)
    py = personal_year(dob)

    numbers = {
        "Life Path": lp, "Birth Day": bd, "Expression": expr,
        "Soul Urge": soul, "Personality": pers, "Maturity": mat,
        "Balance": bal
    }

    # --- Data collected for PDF export ---
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

    # Core numbers for the PDF
    report["core"].append(("Life Path", lp, NUMEROLOGY_DESCRIPTIONS.get(lp, ""),
        [f"Calculation: Month {m_r} + Day {d_r} + Year {y_r} = {lp_total} → {lp}"]))
    report["core"].append(("Expression / Destiny", expr,
        NUMEROLOGY_DESCRIPTIONS.get(expr, ""), None))
    report["core"].append(("Soul Urge / Heart's Desire", soul,
        NUMEROLOGY_DESCRIPTIONS.get(soul, ""), None))
    report["core"].append(("Personality", pers,
        NUMEROLOGY_DESCRIPTIONS.get(pers, ""), None))
    report["core"].append(("Birth Day", bd,
        NUMEROLOGY_DESCRIPTIONS.get(bd, ""), None))
    report["core"].append(("Maturity", mat,
        NUMEROLOGY_DESCRIPTIONS.get(mat, ""), None))
    report["core"].append(("Balance", bal,
        "The number you invoke under stress to regain equilibrium.", None))

    # --- Core profile ---
    print("\n" + "-" * 70)
    print("PART 1: YOUR CORE NUMBERS")
    print("-" * 70)

    print(f"\n>>> LIFE PATH: {lp}")
    print(NUMEROLOGY_DESCRIPTIONS.get(lp, "Unknown"))
    print(f"\nHow it was calculated: Month {m_r} + Day {d_r} + Year {y_r} = {lp_total} → {lp}")

    print(f"\n>>> EXPRESSION / DESTINY: {expr}")
    print(NUMEROLOGY_DESCRIPTIONS.get(expr, "Unknown"))

    print(f"\n>>> SOUL URGE / HEART'S DESIRE: {soul}")
    print(NUMEROLOGY_DESCRIPTIONS.get(soul, "Unknown"))

    print(f"\n>>> PERSONALITY: {pers}")
    print(NUMEROLOGY_DESCRIPTIONS.get(pers, "Unknown"))

    print(f"\n>>> BIRTH DAY: {bd}")
    print(NUMEROLOGY_DESCRIPTIONS.get(bd, "Unknown"))

    print(f"\n>>> MATURITY: {mat}")
    print(NUMEROLOGY_DESCRIPTIONS.get(mat, "Unknown"))

    print(f"\n>>> BALANCE: {bal}")
    print("This is the number you invoke under stress to regain equilibrium.")

    # --- Dynamic synthesis ---
    print("\n" + "-" * 70)
    print("PART 2: DYNAMIC SYNTHESIS (How your numbers interact)")
    print("-" * 70)
    for i, insight in enumerate(synthesize(numbers), 1):
        print(f"\n{i}. {insight}")
        report["synthesis"].append(insight)

    # --- Life area breakdown ---
    print("\n" + "-" * 70)
    print("PART 3: DETAILED LIFE AREA ANALYSIS & ADVICE")
    print("-" * 70)

    areas = ["career", "money", "love", "health", "spirituality", "shadow", "advice"]
    area_titles = {
        "career": "CAREER & PURPOSE",
        "money": "MONEY & FINANCES",
        "love": "LOVE & RELATIONSHIPS",
        "health": "HEALTH & ENERGY",
        "spirituality": "SPIRITUALITY & GROWTH",
        "shadow": "SHADOW & BLIND SPOTS",
        "advice": "DIRECT ADVICE"
    }

    for area in areas:
        print(f"\n### {area_titles[area]} ###")
        area_entries = []
        print("\nFrom your Life Path:")
        txt = advice_for_number(lp, area)
        print(txt)
        area_entries.append(("Life Path", txt))
        if reduce_full(expr) != reduce_full(lp):
            print("\nFrom your Expression:")
            txt = advice_for_number(expr, area)
            print(txt)
            area_entries.append(("Expression", txt))
        if reduce_full(soul) != reduce_full(lp) and reduce_full(soul) != reduce_full(expr):
            print("\nFrom your Soul Urge:")
            txt = advice_for_number(soul, area)
            print(txt)
            area_entries.append(("Soul Urge", txt))
        report["areas"].append((area_titles[area], area_entries))

    # --- Karmic lessons & debts ---
    print("\n" + "-" * 70)
    print("PART 4: KARMIC PATTERNS")
    print("-" * 70)

    kd_meanings = {
        13: "13/4: Learn discipline, work, and honesty. Cutting corners will backfire.",
        14: "14/5: Learn moderation and freedom within limits. Addiction and escapism are the traps.",
        16: "16/7: Learn humility and inner truth. Ego collapse is the lesson.",
        19: "19/1: Learn independence and leadership without domination. You may have to stand alone.",
    }
    if kd:
        print("\nKarmic Debts detected (you are working off old patterns):")
        for label, val in kd:
            meaning = kd_meanings.get(val, "")
            print(f"  - {label}: {val}")
            print(f"    → {meaning}")
            report["karmic_debts"].append((label, val, meaning))
    else:
        print("\nNo Karmic Debts detected in your core numbers. You are not working off a specific old debt in this lifetime.")

    if kl:
        print(f"\nKarmic Lessons (missing numbers in your name): {kl}")
        for n in kl:
            lessons = {
                1: "You must learn to stand alone and assert yourself.",
                2: "You must learn patience, partnership, and sensitivity.",
                3: "You must learn to express yourself and allow joy.",
                4: "You must learn discipline, order, and follow-through.",
                5: "You must learn adaptability, freedom, and moderation.",
                6: "You must learn responsibility, love, and service.",
                7: "You must learn introspection, truth, and faith.",
                8: "You must learn to handle money, power, and authority.",
                9: "You must learn compassion, forgiveness, and letting go."
            }
            print(f"  - Missing {n}: {lessons[n]}")
            report["karmic_lessons"].append((n, lessons[n]))
    else:
        print("\nNo Karmic Lessons — all numbers are present in your name. You have all the tools you need.")

    # --- Hidden passion & subconscious self ---
    print("\n" + "-" * 70)
    print("PART 5: HIDDEN PASSION & SUBCONSCIOUS SELF")
    print("-" * 70)
    print(f"\nHidden Passion: {hp}")
    for n in hp:
        text = NUMEROLOGY_DESCRIPTIONS.get(n, "")[:150]
        print(f"  - {n}: {text}...")
        report["hidden_passion"].append((n, text))
    print(f"\nSubconscious Self: {ss}/9")
    report["subconscious"] = f"{ss}/9"
    if ss <= 3:
        print("  You have a limited subconscious toolkit. Under stress you may feel unequipped. You must consciously learn new responses.")
    elif ss <= 6:
        print("  You have a moderate subconscious toolkit. You have some innate resources but also gaps you must work on.")
    else:
        print("  You have a rich subconscious toolkit. You have many innate resources to draw on under stress.")

    # --- Planes of expression ---
    print("\n" + "-" * 70)
    print("PART 6: PLANES OF EXPRESSION")
    print("-" * 70)
    for plane, count in planes.items():
        print(f"{plane}: {count}")
    dominant = max(planes, key=planes.get)
    print(f"\nDominant plane: {dominant}")
    if dominant == "Physical":
        print("  You are grounded in the body and the material world. You learn by doing.")
    elif dominant == "Mental":
        print("  You are grounded in the mind. You learn by thinking and analyzing.")
    elif dominant == "Emotional":
        print("  You are grounded in feeling. You learn by experiencing and relating.")
    else:
        print("  You are grounded in intuition. You learn by sensing and knowing.")

    # --- Pinnacles & challenges ---
    print("\n" + "-" * 70)
    print("PART 7: PINNACLES & CHALLENGES (Life phases)")
    print("-" * 70)
    print("\nPinnacles (peak opportunities):")
    for num, period in pins:
        text = NUMEROLOGY_DESCRIPTIONS.get(num, "")[:120]
        print(f"  - {period}: {num} — {text}...")
        report["pinnacles"].append((period, num, text))
    print("\nChallenges (lessons to overcome):")
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
        9: "The challenge of compassion — you must learn to let go and forgive."
    }
    for i, c in enumerate(chals, 1):
        meaning = challenge_desc.get(c, "")
        print(f"  - Challenge {i}: {c} — {meaning}")
        report["challenges"].append((i, c, meaning))

    # --- Life cycles ---
    print("\n" + "-" * 70)
    print("PART 8: LIFE CYCLES")
    print("-" * 70)
    for label, c in [("Formative cycle (youth)", cycles[0]),
                     ("Productive cycle (middle age)", cycles[1]),
                     ("Harvest cycle (maturity)", cycles[2])]:
        text = NUMEROLOGY_DESCRIPTIONS.get(c, "")[:150]
        print(f"{label}: {c}")
        print(f"  {text}...")
        report["cycles"].append((label, c, text))

    # --- Personal year ---
    print("\n" + "-" * 70)
    print(f"PART 9: PERSONAL YEAR ({datetime.datetime.now().year})")
    print("-" * 70)
    py_meanings = {
        1: "A year of new beginnings, independence, and planting seeds.",
        2: "A year of patience, partnership, and waiting for seeds to grow.",
        3: "A year of expression, creativity, and social expansion.",
        4: "A year of work, discipline, and building foundations.",
        5: "A year of change, freedom, and unexpected opportunities.",
        6: "A year of responsibility, family, and service.",
        7: "A year of introspection, learning, and spiritual growth.",
        8: "A year of power, money, and achievement.",
        9: "A year of endings, release, and preparing for renewal."
    }
    print(f"Personal Year {py}: {py_meanings.get(py, '')}")
    report["personal_year"] = (py, py_meanings.get(py, ""))
    print("\nThis is the energy shaping your current year. Work with it, not against it.")

    # --- Final blunt summary ---
    print("\n" + "=" * 70)
    print("PART 10: THE BLUNT TRUTH — YOUR CORE CHALLENGE")
    print("=" * 70)
    core_challenge = lp if lp not in MASTER_NUMBERS else reduce_full(lp)
    shadow_raw = ASPECTS.get(core_challenge, ASPECTS[1])["shadow"].rstrip()
    if not shadow_raw.endswith("."):
        shadow_raw += "."
    challenge_text = shadow_raw[0].upper() + shadow_raw[1:]
    advice_text = ASPECTS.get(core_challenge, ASPECTS[1])["advice"]
    print(f"\nBased on your Life Path {lp}, your core life challenge is:")
    print(challenge_text)
    print("\nYour core advice:")
    print(advice_text)
    report["blunt"] = {"challenge": challenge_text, "advice": advice_text}

    print("\n" + "=" * 70)
    print("DISCLAIMER: Numerology is a symbolic system for reflection and")
    print("entertainment. It is not a substitute for professional psychological,")
    print("medical, financial, or legal advice. The 'truths' here are")
    print("archetypal patterns — take what resonates, leave what doesn't.")
    print("=" * 70)

    # --- Write the PDF ---
    pdf_file = generate_pdf_report(report, output_path=pdf_path)
    print(f"\n📄 PDF report saved to: {pdf_file}")
    return pdf_file

# --- Main ---

def run_numerology_analysis():
    print("Welcome to the Detailed Numerology Analyzer!")
    print("-" * 50)
    print("This will produce a long, in-depth report.")
    print("Have your full birth name and birth date ready.")
    print("-" * 50)

    name = input("Enter your FULL BIRTH NAME (as on birth certificate): ").strip()
    while not name or not any(c.isalpha() for c in name):
        print("Please enter a valid name with letters.")
        name = input("Enter your FULL BIRTH NAME: ").strip()

    dob = input("Enter your BIRTH DATE (MMDDYYYY, e.g., 01231990): ").strip()
    while True:
        if len(dob) == 8 and dob.isdigit():
            try:
                datetime.datetime.strptime(dob, "%m%d%Y")
                break
            except ValueError:
                print("Invalid date. Please enter a real date.")
        else:
            print("Invalid format. Enter 8 digits (MMDDYYYY).")
        dob = input("Enter your BIRTH DATE (MMDDYYYY): ").strip()

    safe = "".join(c if c.isalnum() else "_" for c in name)
    default_pdf = f"numerology_report_{safe}.pdf"
    pdf_choice = input(
        f"PDF output filename [{default_pdf}] (press Enter to accept): "
    ).strip()
    pdf_path = pdf_choice or default_pdf
    generate_report(name, dob, pdf_path=pdf_path)

if __name__ == "__main__":
    run_numerology_analysis()