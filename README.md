# LearnAIFast

Source for [learnaifast.in](https://learnaifast.in): practical, beginner-friendly AI guides for students, professionals and small businesses in India.

## What's here

Plain HTML pages with no build step. Each page has its own URL so Google can index it:

- `/` homepage with newsletter signup
- `/guides/` plus three guides: `/what-is-ai/`, `/ai-for-students/`, `/how-to-write-ai-prompts/`
- `/about/`, `/contact/`, `/privacy-policy/`, `/disclaimer/`
- `assets/site.css` and `assets/site.js` are shared by these pages. Old links like `/#prompts` redirect to the new pages.

## SEO

- Every page has a title, meta description, canonical link, social preview tags (`og-image.png`) and structured data (JSON-LD).
- `sitemap.xml` lists every indexable page and `robots.txt` points to it. **When you add a page, add it to `sitemap.xml`.**
- After deploying, submit `https://learnaifast.in/sitemap.xml` in Google Search Console.

## Question papers

The `papers/` folder holds the previous year question papers section: 200 AKTU B.Tech and MCA AI/ML/data papers (2016-17 to 2025-26), each as a full page with every question. Most papers come from the ABESIT question paper bank. To add a paper by hand, follow `papers/HOW-TO-ADD.md`.

## Resume maker

`resume/index.html` is a free one-page resume maker. Visitors paste or upload (.docx, .pdf, .txt) a long resume; it keeps the strongest bullets, drops filler (hobbies, declaration, personal details), fits the result on one A4 page, and lets them edit and save it as PDF. Everything runs in the browser; nothing is uploaded.

## PDF compressor

`compress-pdf/index.html` compresses PDFs in the browser (pdf.js legacy build + pdf-lib): Light / Recommended / Strong presets, or a target size (50 KB, 100 KB, 200 KB, 500 KB, 1 MB) found by stepping resolution and binary-searching JPEG quality. Pages become images, so text is not selectable afterwards. Files are never uploaded.

## File converter

`convert/index.html` converts in the browser: PDF → JPG/PNG/WEBP (multi-page as ZIP), images → PDF (A4/Letter/fit, reorderable), JPG ↔ PNG ↔ WEBP, merging PDFs and images, resize, and per-image size limits (20 KB signature, 50 KB photo, etc.). Quick-preset links like `/convert/#jpg-to-pdf`. Uses pdf.js (legacy), pdf-lib and JSZip. Files are never uploaded.

## Document scanner

`scan/index.html` turns phone photos into scanned PDFs: camera or gallery input, automatic page detection (Otsu threshold + largest region), draggable corners with perspective correction, Clean / Grayscale / Black & white looks with lighting correction, rotate, multi-page reorder, and export to PDF (A4 or fit, optional size limit) or JPG/ZIP. Uses pdf-lib and JSZip. Photos are never uploaded.

## Run locally

Run `python3 -m http.server` in this folder and open http://localhost:8000 (links use root paths like `/about/`, so opening the file directly won't follow them).

## Deploy

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Hostinger). For GitHub Pages: Settings → Pages → deploy from the `main` branch, root folder. Then add `learnaifast.in` as the custom domain and update the DNS records in GoDaddy.

## Before going live

- Add your name and a short bio in "Who's behind LearnAIFast" on `about/index.html`
- Connect the newsletter form to an email tool such as Mailchimp
