# LearnAIFast

Source for [learnaifast.in](https://learnaifast.in): practical, beginner-friendly AI guides for students, professionals and small businesses in India.

## What's here

`index.html` is the whole site in one file, with no build step. It includes:

- Homepage with newsletter signup
- Three guides: What Is AI?, 10 Ways Students Can Use AI, How to Write Better AI Prompts
- About, Contact, Privacy Policy and Disclaimer pages

Pages switch with links like `#about` and `#prompts`.

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

Open `index.html` in any browser. No server needed.

## Deploy

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Hostinger). For GitHub Pages: Settings → Pages → deploy from the `main` branch, root folder. Then add `learnaifast.in` as the custom domain and update the DNS records in GoDaddy.

## Before going live

- Replace `[Your Name]` on the About page
- Replace `[Date]` in the Privacy Policy and Disclaimer
- Connect the newsletter form to an email tool such as Mailchimp
