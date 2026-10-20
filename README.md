# LearnAIFast

Source for [learnaifast.in](https://learnaifast.in): practical, beginner-friendly AI guides for students, professionals and small businesses in India.

## What's here

`index.html` is the whole site in one file, with no build step. It includes:

- Homepage with newsletter signup
- Three guides: What Is AI?, 10 Ways Students Can Use AI, How to Write Better AI Prompts
- About, Contact, Privacy Policy and Disclaimer pages

Pages switch with links like `#about` and `#prompts`.

## Question papers

The `papers/` folder holds the previous year question papers section. To add a paper, follow `papers/HOW-TO-ADD.md`.

## Run locally

Open `index.html` in any browser. No server needed.

## Deploy

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Hostinger). For GitHub Pages: Settings → Pages → deploy from the `main` branch, root folder. Then add `learnaifast.in` as the custom domain and update the DNS records in GoDaddy.

## Before going live

- Replace `[Your Name]` on the About page
- Replace `[Date]` in the Privacy Policy and Disclaimer
- Connect the newsletter form to an email tool such as Mailchimp
