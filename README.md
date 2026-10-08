# BorderSight

> BorderSight helps immigration officers quickly verify a traveler’s passport, visa, identity, and security information, highlighting anything that may need a closer look.

## Team

**Team Name:** [TetraByte]


| Member | Contribution   |
| ------ | -------------- |
| Akhilesh Aravind J | Backend and Verification |
| Sharvesh J B  | FrontEnd and Deployment |
| Roahith P | AI and Decision engine |
| Gaurav T | Document Intelligence |


## Problem Statement

### The Problem

Immigration officers often rely on multiple manual checks to verify passports, visas, identities, and security information, making screening slower and increasing the chance of missed inconsistencies.

### Why We Chose This Problem

We chose this problem because immigration screening involves sensitive decisions where missed inconsistencies can create security risks. BorderSight aims to make these checks faster, more consistent, and easier for officers to review.

## Solution
BorderSight brings passport, visa, identity, and security checks into one workflow, helping officers quickly identify mismatches and cases that need further review.
### Key Features

- Passport and visa verification
- Identity and face matching
- Security record screening
- Risk-based screening results for officer review

## Innovation and Differentiation

BorderSight combines multiple verification checks into one workflow instead of relying on separate manual checks. It uses structured evidence and AI-assisted analysis to highlight inconsistencies while keeping the final decision with the human officer.

## Technical Implementation

### Architecture
![.](https://github.com/Roahith/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club/blob/main/artart.jpeg?raw=true)




### Technology Stack


| **Category** | **Technologies** |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | JSON-based synthetic databases |
| AI / ML | Gemma 4, OCR/MRZ processing, face verification |
| Infrastructure | Vercel, Render |
| APIs / Services | REST API, FastAPI endpoints |



### How It Works

BorderSight consists of a web frontend and FastAPI backend. The backend handles passport, visa, security, and identity checks, combines the results into evidence, and produces a final screening result for the officer.

### Technical Decisions

Modular backend: Passport, visa, security, document, and AI checks are kept as separate modules so they can be tested and changed independently.
Evidence-based decisions: Screening results are combined into a single risk result instead of letting the AI make the decision on its own.
Synthetic data: We used demo databases and documents to safely demonstrate the workflow without relying on real government or security records.
Human-in-the-loop: BorderSight flags cases for officer review rather than automatically making immigration decisions.
Simple architecture: JSON-based storage and FastAPI were chosen to keep the prototype fast to build, test, and deploy during the hackathon.
## Implementation During the Hackathon

During the Hack Day, we built the main BorderSight workflow from scratch. We added passport and visa checks, security screening, face verification, demo documents and databases, the FastAPI backend, and the officer dashboard.

### Team Contributions

- **Roahith P:** AI, risk scoring, and decision logic
- **Gaurav T:** Passport OCR, MRZ, and document verification
- **Sharvesh J B:** Frontend dashboard and screening interface
- **Akhilesh Aravind J:** Backend, immigration/security checks, and demo documents

## Working Application

**Live Application:** [Live URL]

[Briefly explain how the deployed application can be accessed and what functionality can be tested.]

The submitted application should be functional and accessible through the provided link where applicable.

## Demo Video

**Demo Video:** [Video URL]

[Provide a short demonstration of the working project, covering the main user flow and important functionality.]

## Open Source and AI Usage

### AI / Models

- Gemma 4: Used to analyse the screening results and explain the final result to the officer.

### Open Source Components

- FastAPI: Backend API and screening workflow.
- React + Vite: Frontend dashboard and user interface.
- OpenCV: Face verification and image processing.
- OCR / MRZ tools: Extract passport details and validate MRZ data.
- Synthetic dataset: Demo passport, visa, and security records used for testing.

## Setup and Usage

### Prerequisites

Node.js and npm
Python 3.10+

### Installation

```bash
git clone [repository-url]
cd [project-directory]
[installation-command]
```

### Environment Variables

```env
[VARIABLE_NAME]=[value]
```



### Running the Project

```bash
[run-command]
```

### Usage

1. Open the BorderSight web app.
2. Create or select a test traveler.
3. Upload the passport and visa documents.
4. Run the screening process.
5. Review the passport, visa, security, and identity checks.
6. Check the final result and reasons shown by BorderSight.

## Devpost Submission

**Devpost Project:** [Devpost Project URL]

[Add the link to the team's Devpost submission. Ensure the Devpost project page is complete and contains the required project information, links, media, and team details.]

## Credits and License

### Credits

FastAPI, React, Vite, Gemma 4, OpenCV, OCR/MRZ tools, synthetic datasets, Hacktoberfest.

### License

MIT License.

## Submission Checklist

- [ ] Project title and description added
- [ ] All team members listed
- [ ] Problem clearly explained
- [ ] Reason for choosing the problem explained
- [ ] Solution and key features documented
- [ ] Innovation and differentiation explained
- [ ] Architecture included
- [ ] Technical implementation documented
- [ ] Work completed during the hackathon documented
- [ ] Team contributions documented
- [ ] Working application is functional
- [ ] Live application link added where applicable
- [ ] Demo video added
- [ ] AI and open-source components documented
- [ ] Setup and usage instructions tested
- [ ] Challenges and learnings documented
- [ ] Devpost submission completed
- [ ] Devpost link added
- [ ] Credits added
- [ ] License added
- [ ] Repository is organized and complete
