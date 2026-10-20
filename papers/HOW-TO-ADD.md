# How to add a question paper

Each paper needs three things: the PDF, a page for it, and one line in the list.

## 1. Add the PDF

Put the file in `papers/pdfs/`. Use a clear name in lowercase with dashes:

```
aktu-btech-machine-learning-2024.pdf
```

Keep each file under 100 MB (a GitHub limit). Most scanned papers are 1–5 MB.

## 2. Make the paper page

1. Copy `papers/_template.html` (or a finished page like `aktu-btech-machine-learning-techniques-kcs055-2023-24.html`) and rename it to match the PDF, e.g. `aktu-btech-machine-learning-2024.html`.
2. In the copy:
   - **Delete** the line `<meta name="robots" content="noindex">` so Google can list the page.
   - **Delete** the yellow `<div class="banner">…</div>` example notice.
   - Update the `<title>`, `<meta name="description">`, breadcrumb, heading and the facts table.
   - Point the Download PDF button at your PDF: `pdfs/aktu-btech-machine-learning-2024.pdf`.
   - Type the questions into Section A and Section B. Text questions are what Google ranks, so don't skip this.
   - Update "Most repeated topics". Bar width = years asked ÷ 5 × 100%, e.g. 3 of 5 → `width:60%`.
   - Write 3–5 answer hints for the most important questions.
   - Point "Related papers" at other real pages.

Tip: ask an AI tool to turn the PDF into text, and to count which topics repeat across 5 years of papers. Always check its output against the original paper.

## 3. Add it to the list

Open `papers/data.js` and add one line inside `PAPERS`:

```js
{ university: "AKTU", course: "B.Tech", subject: "Machine Learning", code: "KCS-055", year: 2024, session: "Dec 2024", semester: "5th", page: "aktu-btech-machine-learning-2024.html" },
```

`subject` must match a name in `SUBJECTS` exactly. To add a new subject, add it to `SUBJECTS` too.

To list a paper without its own page (PDF only), leave out `page` and add `pdf: "link to the PDF"`.

## 4. Publish

Commit and push to `main`. GitHub Pages updates the site in about a minute.

## Copyright

Only upload papers that are publicly available or shared with you by students. Always fill in the Source row. Remove any paper promptly if the university asks.
