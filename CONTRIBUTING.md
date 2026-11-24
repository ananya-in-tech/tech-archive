# Contributing to Tech Archive

Thank you for helping make Tech Archive a useful, reliable, and welcoming technical knowledge library.

Tech Archive welcomes contributions from students, developers, educators, and practitioners. You can contribute original notes, curated links, course recommendations, practice material, diagrams, project references, and improvements to repository tooling.

## What makes a good contribution?

- **Useful:** It helps a learner understand a concept or take a meaningful next step.
- **Credible:** It links to an authoritative source or identifies the author's experience and context.
- **Clear:** It includes a concise description, prerequisites, and an appropriate difficulty level where relevant.
- **Maintained:** Time-sensitive resources include a version, publication date, or last-checked date where appropriate.
- **Accessible:** Notes use semantic Markdown headings; diagrams include alt text and a text explanation.
- **Responsible:** Do not upload copyrighted books, paid course material, private data, credentials, or malicious content.

## Where should content go?

Place material in the closest subject directory:

| Contribution | Location |
| --- | --- |
| Mathematics and learning fundamentals | `01-foundations/` |
| Programming languages and paradigms | `02-programming/` |
| DSA and core CS subjects | `03-computer-science/` |
| Web, mobile, desktop, and API development | `04-software-development/` |
| AI, ML, data science, cybersecurity, blockchain, and cloud | `05-emerging-technologies/` |
| System design, architecture, testing, and DevOps | `06-engineering-practices/` |
| Coding and technical interview preparation | `07-interview-preparation/` |
| Resumes, internships, job search, and open source | `08-career-resources/` |
| Project ideas, case studies, and practical exercises | `09-projects-and-practice/` |
| Learning sequences and roadmaps | `10-learning-roadmaps/` |

Keep a resource with its subject. If it is relevant in multiple places, link to the canonical copy rather than duplicating it.

## Recommended subject structure

Use only the subdirectories that make sense for the subject. A typical example:

```text
subject-name/
├── README.md
├── notes/
├── courses/
├── books/
├── research-papers/
├── practice/
├── interview-questions/
├── references/
└── assets/
    ├── diagrams/
    ├── images/
    └── datasets/
```

Do not create empty folders just to match this example. A subject README should act as its index and explain what is available.

## Adding a curated external resource

Add entries to the relevant subject README using a consistent description:

```markdown
### Resource title

- **Type:** Course / Documentation / Book / Article / Tool / Paper
- **Level:** Beginner / Intermediate / Advanced / All levels
- **Cost:** Free / Freemium / Paid / Not specified
- **Link:** [Open resource](https://example.com)
- **Why it is useful:** One or two sentences describing its value.
- **Prerequisites:** Concepts a learner should know first, if any.
- **Last checked:** YYYY-MM (for resources likely to change)
```

Do not claim that a resource is free unless you have checked its current access terms. Clearly disclose registration, subscription, or payment requirements where known.

## Writing Markdown notes

Prefer Markdown over screenshots or scanned documents. A useful note often includes:

```markdown
# Topic title

## Overview
What the topic is and why it matters.

## Prerequisites
What the learner should know first.

## Core concepts
Explain the important ideas with examples.

## Practical examples
Show how the concepts are applied.

## Common mistakes
Highlight pitfalls and edge cases.

## Further reading
Link to authoritative sources.

## References
Credit sources used.
```

Keep each note focused. Use diagrams where they improve understanding and include descriptive alt text.

## Adding PDFs and other files

- Upload only files you created or are permitted to redistribute.
- Link to commercial books, paid courses, and copyrighted materials instead of committing copies.
- Use descriptive names such as `process-scheduling-notes.pdf`.
- Keep supporting images, diagrams, and datasets in the relevant subject's `assets/` directory.
- Avoid committing generated files, executables, archives, or very large datasets unless they are essential and approved.
- For binary files that are useful as standalone learning material, document their purpose and source in the subject README.

## Pull request workflow

1. Fork the repository.
2. Create a focused branch, for example `docs/os-process-management` or `feat/ai-learning-resources`.
3. Add content in the correct subject directory.
4. Check links, spelling, Markdown formatting, and file names.
5. Submit a pull request describing what changed, why it is useful, and the sources used.
6. Respond constructively to review feedback.

Never commit directly to `main`.

## Review checklist

Before opening a pull request, confirm:

- [ ] The content is in the correct subject directory.
- [ ] The title and filename are descriptive.
- [ ] External links work and point to the intended resource.
- [ ] Sources and authors are credited.
- [ ] Copyright and redistribution permissions are respected.
- [ ] No secrets, credentials, private data, or harmful payloads are included.
- [ ] The relevant subject README is updated.
- [ ] The change does not duplicate an existing resource.

## Community conduct

Be respectful, inclusive, patient, and constructive. Critique ideas and content, not people. Follow the repository [Code of Conduct](.github/CODE_OF_CONDUCT.md).

Thank you for sharing knowledge and helping others grow.
