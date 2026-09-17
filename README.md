# 🔮 Detailed Numerology Analyzer

A command-line Python tool that computes a comprehensive numerology profile
from your **full birth name** and **birth date**, prints a detailed report to
your terminal, and exports the same report as a **polished PDF**.

The analysis is unusually blunt and archetypal — it includes shadow sides,
karmic patterns, life-phase forecasts, and direct advice across career, money,
love, health, spirituality, and personal growth.

> ⚠️ **Disclaimer:** Numerology is a symbolic system for reflection and
> entertainment. It is **not** a substitute for professional psychological,
> medical, financial, or legal advice. The "truths" here are archetypal
> patterns — take what resonates, leave what doesn't.

---

## ✨ Features

### Core numbers
- **Life Path** — your overarching life purpose
- **Expression / Destiny** — your natural talents and outward gifts
- **Soul Urge / Heart's Desire** — what you truly want inside
- **Personality** — how others first perceive you
- **Birth Day** — a special talent you were born with
- **Maturity** — the energy that unfolds in the second half of life
- **Balance** — the number you invoke under stress

### Advanced numerology
- **Karmic Debts** — detection of 13 / 14 / 16 / 19 in raw sums
- **Karmic Lessons** — numbers missing from your name
- **Hidden Passion** — the most frequent letter values in your name
- **Subconscious Self** — how many of the 9 numbers appear in your name
- **Planes of Expression** — Physical / Mental / Emotional / Intuitive balance
- **Pinnacles** — four peak-opportunity life phases with age ranges
- **Challenges** — four core lessons you must overcome
- **Life Cycles** — Formative / Productive / Harvest cycles
- **Personal Year** — the current-year energy shaping your life

### Dynamic synthesis
The tool cross-references your numbers to reveal:
- Life Path vs Expression tension (talent vs purpose)
- Soul Urge vs Personality gap (how you feel vs how you appear)
- Life Path vs Soul Urge tension (want vs need)
- How your Birth Day, Maturity, and Balance numbers color the whole chart

### Deep life-area advice
Every core number contributes tailored advice across **seven life areas**:
- 💼 Career & Purpose
- 💰 Money & Finances
- ❤️ Love & Relationships
- 🩺 Health & Energy
- 🧘 Spirituality & Growth
- 🌑 Shadow & Blind Spots
- 🎯 Direct Advice

### Blunt truth section
A closing "core challenge" built from the shadow side of your Life Path,
paired with one concrete action to work on it.

### PDF export
A multi-section, professionally formatted PDF with:
- Cover page (name + birth date)
- Section headers with horizontal rules
- Bold and italic inline formatting
- Clean bullet lists
- A styled **Planes of Expression** table
- Page numbers in the footer

---

## 📦 Requirements

- **Python 3.8+** (tested on 3.11)
- **reportlab** — the only external dependency

All other imports (`datetime`, `io`, `os`, `re`, `itertools`) are part of the
Python standard library.

### `requirements.txt`

```txt
reportlab>=3.6,<5
```

---

## 🚀 Installation

### 1. Clone or download the project

Put `numerology.py` and `requirements.txt` in the same folder.

### 2. Install dependencies

**Windows (PowerShell / CMD):**
```bat
"C:\Program Files\Python311\python.exe" -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m pip install -r requirements.txt
```

**Or with a virtual environment (recommended):**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Verify reportlab is installed

```bash
python -c "import reportlab; print('reportlab', reportlab.Version)"
```

---

## ▶️ Usage

Run the script:

```bash
python numerology.py
```

You will be prompted for:

1. **Your full birth name** — as it appears on your birth certificate
   (e.g. `Souparna Paul`). Middle names matter.
2. **Your birth date** in `MMDDYYYY` format (e.g. `11212000` for Nov 21, 2000).
3. **A PDF output filename** — press Enter to accept the default
   (`numerology_report_<Your_Name>.pdf`).

### Example session

```
Welcome to the Detailed Numerology Analyzer!
--------------------------------------------------
This will produce a long, in-depth report.
Have your full birth name and birth date ready.
--------------------------------------------------
Enter your FULL BIRTH NAME (as on birth certificate): Souparna Paul
Enter your BIRTH DATE (MMDDYYYY, e.g., 01231990): 11212000
PDF output filename [numerology_report_Souparna_Paul.pdf] (press Enter to accept):

======================================================================
               DETAILED NUMEROLOGY ANALYSIS
======================================================================
Name: Souparna Paul
Birth Date: 11/21/2000
======================================================================
...
📄 PDF report saved to: /home/user/numerology_report_Souparna_Paul.pdf
```

The full report prints to the console **and** is saved as a PDF in the same
folder as the script (or wherever you specify).

---

## 📁 Project structure

```
your-project/
├── numerology.py            # main program
├── requirements.txt         # dependencies
├── README.md                # this file
└── numerology_report_*.pdf  # generated PDFs
```

---

## 🧠 How the numerology is calculated

### Letter values (Pythagorean system)

| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| A | B | C | D | E | F | G | H | I |
| J | K | L | M | N | O | P | Q | R |
| S | T | U | V | W | X | Y | Z |   |

### Master Numbers
The numbers **11, 22, and 33** are considered *Master Numbers* and are **not**
reduced to a single digit. They carry extra intensity and spiritual weight.

### Reduction
A number is reduced by summing its digits repeatedly until it is either a
single digit (1–9) or a Master Number (11, 22, 33).

Example: `2000 → 2 + 0 + 0 + 0 = 2`

### Life Path
```
Life Path = reduce( reduce(MM) + reduce(DD) + reduce(YYYY) )
```

### Expression / Soul Urge / Personality
- **Expression** = sum of *all* letters in the full name
- **Soul Urge** = sum of *vowels* only (A, E, I, O, U — plus Y when it sounds
  like a vowel)
- **Personality** = sum of *consonants* only

### Maturity
```
Maturity = reduce( reduce(Life Path) + reduce(Expression) )
```

### Balance
```
Balance = reduce( sum of the FIRST letter of each name part )
```

### Karmic Debts
Detected when any of these raw (pre-reduction) sums equals **13, 14, 16, or 19**:
- Life Path raw sum
- Birth day
- Birth year
- Expression raw sum
- Soul Urge raw sum
- Personality raw sum

### Pinnacles and Challenges
Derived from reduced Month, Day, and Year using standard Pythagorean
numerology formulas, with age ranges based on the Life Path first cycle.

---

## 🔧 Customization

### Add or change life-area advice
Edit the `ASPECTS` dictionary. Each key is a number (1–9, 11, 22, 33) and each
value is a dict with these keys:

```python
"career", "money", "love", "health",
"spirituality", "shadow", "advice"
```

### Change descriptions
Edit `NUMEROLOGY_DESCRIPTIONS` to rewrite the base personality text for any
number.

### Change PDF styling
Edit `_pdf_styles()` to adjust fonts, colors, sizes, and spacing. The style
names are `title`, `subtitle`, `h1`, `h2`, `body`, `bullet`, `quote`, and
`small`.

### Change page size / margins
In `generate_pdf_report()`, modify the `SimpleDocTemplate` arguments:
```python
doc = SimpleDocTemplate(
    output_path, pagesize=LETTER,
    leftMargin=0.85 * inch, rightMargin=0.85 * inch,
    topMargin=0.85 * inch, bottomMargin=0.85 * inch,
    ...
)
```
Swap `LETTER` for `A4` (imported from `reportlab.lib.pagesizes`) if you prefer
A4 paper.

### Toggle Y as a vowel
Adjust `is_vowel()` if you want a stricter or looser rule for treating `Y` as a
vowel. By default, Y is a vowel when surrounded by consonants or at the end of
the name.

---

## 🛠️ Troubleshooting

### `ModuleNotFoundError: No module named 'reportlab'`
You didn't install the dependency. Run:
```bash
pip install -r requirements.txt
```

### `SyntaxError: invalid syntax` on a description line
Caused by nested double quotes inside a double-quoted string. Either escape
them (`\"`) or use single quotes for the outer string, or wrap the value in
triple quotes (`"""..."""`).

### PDF shows literal `<b>` and `</b>` tags
Your `_esc()` helper is escaping markup it shouldn't. Make sure the
whitelist-regex version is in place (see the code around `_ALLOWED_TAGS`).

### PDF pages are flooded with `1 1 1 1 1 ...`
That's an artifact of `HRFlowable` being read by some PDF text extractors as
a stream of dash glyphs. The provided `_hr()` implementation renders rules as
1-row tables with a bottom border instead, which avoids the artifact.

### `AttributeError: 'NoneType' object has no attribute 'replace'`
`re.split()` returned a `None` chunk. The current `_esc()` skips `None` chunks
— make sure your copy does too.

### PDF isn't created / file path looks wrong
The script prints the absolute path of the saved PDF at the end of the run.
Check that folder for write permissions. On Windows, avoid saving to
`C:\Program Files\`; use `Documents` or the script's own folder.

---

## 🗺️ Roadmap / possible extensions

- [ ] Compatibility mode: compare two charts side by side
- [ ] Personal **Month** and **Day** forecasts
- [ ] JSON / CSV export of the raw numbers
- [ ] Multi-language output (i18n)
- [ ] Optional `fpdf2` backend for a lighter dependency footprint
- [ ] Chart diagrams (pie chart for Planes of Expression)
- [ ] Unit tests for the numerology math

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Commit your changes: `git commit -am "Add my change"`.
4. Push to the branch: `git push origin feature/my-change`.
5. Open a Pull Request.

Please keep the style consistent with the existing code (PEP 8, docstrings on
public functions, clear variable names).

---

## 📜 License

This project is provided as-is for personal and educational use. No warranty
is provided. You may modify and redistribute it freely.

If you publish a fork, a credit link back is appreciated.

---

## 🙏 Acknowledgements

- Pythagorean numerology tradition
- The [reportlab](https://www.reportlab.com/) team for the PDF toolkit
- Everyone who uses this for honest self-reflection rather than fortune-telling

---

## 📞 Contact

If you find a bug or want a new feature, open an issue on the project's
repository. For numerology questions, the tool itself is the best answer —
run it, read the report, and see what resonates.

**Remember: the numbers don't decide your life. You do.**
