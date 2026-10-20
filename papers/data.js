/*
  LearnAIFast question papers list.
  To add a paper, copy one line inside PAPERS and change the values.
  See papers/HOW-TO-ADD.md for the full steps.

  Fields:
    university  e.g. "AKTU", "JNTUH", "VTU"
    course      "B.Tech" or "M.Tech"
    subject     must match a name in SUBJECTS below
    code        subject code printed on the paper, e.g. "KCS-055"
    year        exam year, e.g. 2024
    session     e.g. "Dec 2024" or "May 2024"
    semester    e.g. "5th"
    page        link to the paper page, e.g. "aktu-btech-machine-learning-2024.html"
    sample      true only for the example page; remove that line once real papers are added
*/
window.SUBJECTS = [
  "Machine Learning",
  "Artificial Intelligence",
  "Deep Learning",
  "Data Science",
  "Natural Language Processing",
  "Computer Vision",
  "Soft Computing",
  "Data Mining",
  "Python Programming"
];

window.PAPERS = [
  { university: "Example University", course: "B.Tech", subject: "Machine Learning", code: "ML-501", year: 2024, session: "Dec 2024", semester: "5th", page: "example-btech-machine-learning-2024.html", sample: true }
];
