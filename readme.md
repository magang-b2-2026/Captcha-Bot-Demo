# CAPTCHA Bot Website

An automated CAPTCHA detection, OCR recognition, CAPTCHA solving, and web form interaction system built with Python, Playwright, PaddleOCR, EasyOCR, and OpenCV.

This project is developed as an experimental automation and computer vision project for studying how OCR systems perform on different CAPTCHA image conditions, including normal text CAPTCHA, mathematical CAPTCHA, and noisy image CAPTCHA.

The system combines webpage analysis, CAPTCHA detection, image preprocessing, multiple OCR engines, OCR candidate ranking, CAPTCHA classification, CAPTCHA solving, automated form interaction, and result evaluation into a single workflow.

> [!WARNING]
> This project is intended for educational purposes, authorized testing, personal projects, and controlled demo or staging environments only. Do not use this system to bypass CAPTCHA, anti-bot mechanisms, access controls, or other security protections on websites without explicit authorization.

---

## Table of Contents

- [Overview](#overview)
- [Objectives](#objectives)
- [Features](#features)
- [System Architecture](#system-architecture)
- [System Workflow](#system-workflow)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Supported Demo Environments](#supported-demo-environments)
- [Page Analyzer](#page-analyzer)
- [CAPTCHA Detection](#captcha-detection)
- [OCR Pipeline](#ocr-pipeline)
- [Image Preprocessing](#image-preprocessing)
- [OCR Candidate Ranking](#ocr-candidate-ranking)
- [CAPTCHA Solvers](#captcha-solvers)
- [Form Interaction](#form-interaction)
- [Submission Result Detection](#submission-result-detection)
- [Evaluation and Metrics](#evaluation-and-metrics)
- [Debug Output](#debug-output)
- [Testing](#testing)
- [Example Execution](#example-execution)
- [Example OCR Candidate Ranking](#example-ocr-candidate-ranking)
- [Experimental Results](#experimental-results)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Ethical and Legal Considerations](#ethical-and-legal-considerations)
- [License](#license)

---

## Overview

CAPTCHA systems are commonly used by websites to distinguish human users from automated programs.

From a computer vision and automation perspective, image-based CAPTCHA provides an interesting test case for evaluating OCR systems under different visual conditions.

CAPTCHA images can contain:

- Randomized characters
- Background noise
- Distortion
- Low contrast
- Interfering lines
- Colored backgrounds
- Different fonts
- Character spacing variations
- Image artifacts

This project explores an automated pipeline that attempts to recognize and process supported CAPTCHA challenges in authorized demo and testing environments.

The project does not rely on a single OCR prediction. Instead, the system generates multiple image preprocessing variants, runs multiple OCR engines, collects OCR candidates, and ranks the candidates using several signals.

The overall system consists of:

```text
Web Automation
       ↓
Page Analysis
       ↓
CAPTCHA Detection
       ↓
CAPTCHA Image Capture
       ↓
Image Preprocessing
       ↓
Multiple OCR Engines
       ↓
Candidate Collection
       ↓
Candidate Ranking
       ↓
CAPTCHA Classification
       ↓
CAPTCHA Solving
       ↓
Form Interaction
       ↓
Submission Result Detection
       ↓
Evaluation Logging
```

---

## Objectives

The main objectives of this project are:

1. Build a reusable webpage analyzer for identifying CAPTCHA-related elements.
2. Experiment with OCR recognition on CAPTCHA images.
3. Compare OCR results from different preprocessing techniques.
4. Combine multiple OCR engines into a single recognition pipeline.
5. Develop a candidate-ranking mechanism instead of relying on a single OCR result.
6. Automatically distinguish between supported CAPTCHA types.
7. Implement basic CAPTCHA solvers for supported demo cases.
8. Automate form interaction using Playwright.
9. Measure CAPTCHA processing time and submission results.
10. Create a foundation for further experimentation with OCR robustness.

---

## Features

### Web Automation

- Browser automation using Playwright.
- Automatic webpage navigation.
- Automatic CAPTCHA element detection.
- Automatic CAPTCHA image capture.
- Automatic form field detection.
- Automatic form filling.
- Automatic form submission.
- Submission result detection.

### CAPTCHA Detection

The current detector supports:

```text
TEXT
MATH
UNKNOWN
```

### OCR

The project uses two OCR engines:

- PaddleOCR
- EasyOCR

The two OCR engines provide independent recognition results that can be compared during candidate ranking.

### Image Preprocessing

The OCR pipeline generates multiple image variants:

- Original
- Grayscale
- Contrast enhancement
- Otsu threshold
- Inverted Otsu threshold
- Adaptive threshold
- Sharpening
- Saturation mask
- Blue mask

### CAPTCHA Solving

Currently supported:

- Text CAPTCHA recognition
- Basic mathematical CAPTCHA

Mathematical operators supported:

```text
+
-
*
/
```

The solver also normalizes common multiplication representations:

```text
X
x
×
```

### Evaluation

The system records:

- Timestamp
- URL
- CAPTCHA type
- OCR result
- Answer
- Submission result
- Processing time

Results are stored in CSV format.

---

## System Architecture

The complete architecture can be represented as follows:

```text
                         ┌─────────────────────┐
                         │     Target URL      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Playwright      │
                         │  Browser Automation  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Page Analyzer    │
                         │                     │
                         │ • CAPTCHA Input     │
                         │ • CAPTCHA Image     │
                         │ • Submit Button     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  CAPTCHA Capture    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │     Image Preprocessing      │
                    │                              │
                    │ Original                     │
                    │ Grayscale                    │
                    │ Contrast                     │
                    │ Otsu                        │
                    │ Otsu Inverted               │
                    │ Adaptive Threshold           │
                    │ Sharpen                      │
                    │ Saturation Mask              │
                    │ Blue Mask                    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │          OCR Layer            │
                    │                              │
                    │      PaddleOCR + EasyOCR     │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │    OCR Candidate Ranking     │
                    │                              │
                    │ • Confidence                 │
                    │ • Voting                     │
                    │ • Engine Agreement           │
                    │ • Variant Agreement          │
                    │ • Shape Score                │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │     CAPTCHA Detector         │
                    │                              │
                    │ TEXT / MATH / UNKNOWN        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │   Text Solver    │          │   Math Solver    │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Form Handler      │
                       │                     │
                       │ Fill → Submit       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Result Detection    │
                       │                     │
                       │ SUCCESS / FAILED    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Metrics Logger    │
                       │                     │
                       │    results.csv      │
                       └─────────────────────┘
```

---

## System Workflow

The main execution flow is:

```text
1. User enters target URL
              ↓
2. Playwright opens webpage
              ↓
3. Page Analyzer inspects webpage
              ↓
4. CAPTCHA input is detected
              ↓
5. CAPTCHA image is detected
              ↓
6. Submit button is detected
              ↓
7. Required non-CAPTCHA fields are filled
              ↓
8. CAPTCHA image is captured
              ↓
9. Image preprocessing generates variants
              ↓
10. PaddleOCR processes image variants
              ↓
11. EasyOCR processes image variants
              ↓
12. OCR candidates are collected
              ↓
13. Candidates are normalized and ranked
              ↓
14. CAPTCHA type is detected
              ↓
15. Appropriate solver is selected
              ↓
16. CAPTCHA answer is inserted
              ↓
17. Form is submitted
              ↓
18. Submission result is detected
              ↓
19. Processing metrics are saved
```

---

## Project Structure

```text
Captcha Bot Website/
│
├── .venv/
│
├── browser/
│   ├── __init__.py
│   ├── browser_manager.py
│   └── page_analyzer.py
│
├── detector/
│   ├── __init__.py
│   └── captcha_detector.py
│
├── evaluation/
│   ├── __init__.py
│   └── metrics.py
│
├── interaction/
│   ├── __init__.py
│   └── form_handler.py
│
├── outputs/
│   ├── captcha_images/
│   │   ├── debug/
│   │   └── ocr_temp/
│   │
│   └── logs/
│
├── solver/
│   ├── __init__.py
│   ├── math_solver.py
│   ├── paddle_solver.py
│   └── text_solver.py
│
├── main.py
├── requirements.txt
├── test_analyzer.py
└── test_detector.py
```

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `browser/` | Browser automation and webpage analysis |
| `browser/page_analyzer.py` | Detect CAPTCHA input, CAPTCHA image, and submit button |
| `detector/` | CAPTCHA type classification |
| `detector/captcha_detector.py` | Detect text, math, or unknown CAPTCHA |
| `solver/` | OCR and CAPTCHA solving |
| `solver/paddle_solver.py` | Multi-engine OCR and candidate ranking |
| `solver/math_solver.py` | Mathematical expression solving |
| `solver/text_solver.py` | Text CAPTCHA processing |
| `interaction/` | Form interaction |
| `interaction/form_handler.py` | Filling normal fields and CAPTCHA fields |
| `evaluation/` | Metrics and experiment logging |
| `evaluation/metrics.py` | CSV result logging |
| `outputs/` | Debug images and experiment results |
| `main.py` | Main end-to-end workflow |

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Browser Automation | Playwright |
| Primary OCR | PaddleOCR |
| Secondary OCR | EasyOCR |
| Image Processing | OpenCV |
| Deep Learning Backend | PaddlePaddle / PyTorch |
| Data Logging | CSV |
| Development Environment | Visual Studio Code |
| Operating System | Windows |

---

## Requirements

The project is designed primarily for Windows.

Recommended environment:

- Python 3.10+
- Google Chrome / Chromium
- Visual Studio Code
- PowerShell
- Git

Python dependencies are listed in:

```text
requirements.txt
```

The project uses packages including:

```text
playwright
paddleocr
paddlepaddle
easyocr
opencv-python
torch
```

The exact package versions should follow the versions specified in `requirements.txt`.

---

# Installation

## 1. Clone the Repository

```powershell
git clone <YOUR_REPOSITORY_URL>
```

Navigate to the project directory:

```powershell
cd "Captcha Bot Website"
```

---

## 2. Create Virtual Environment

```powershell
python -m venv .venv
```

---

## 3. Activate Virtual Environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

A successful activation should look similar to:

```text
(.venv) PS C:\Users\ACER\Captcha Bot Website>
```

---

## 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 5. Install Playwright Browser

Install Chromium:

```powershell
playwright install chromium
```

---

# Running the Project

After activating the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python main.py
```

The program will ask for a website URL:

```text
Enter website URL:
```

Enter an authorized CAPTCHA demonstration or testing URL.

For example:

```text
http://democaptcha.com/demo-form-eng/math-image.html
```

The system will then execute the complete workflow.

---

# Supported Demo Environments

The project has been tested during development using several public CAPTCHA demonstration environments.

> [!NOTE]
> Demo websites may change their HTML structure, CAPTCHA content, or availability over time. Therefore, previously successful selectors or results may not always remain identical.

---

## 1. Normal Text CAPTCHA

Demo:

```text
https://2captcha.com/demo/normal
```

This page contains a normal image-based CAPTCHA.

Relevant elements used during development included:

```text
CAPTCHA image
Enter text from the image
Check
```

An example CAPTCHA encountered during testing was:

```text
W9H5K
```

The OCR pipeline was able to recognize this CAPTCHA correctly using PaddleOCR after OCR configuration improvements.

---

## 2. Mathematical CAPTCHA

Demo:

```text
http://democaptcha.com/demo-form-eng/math-image.html
```

Example challenge:

```text
21+42=?
```

The workflow is:

```text
21+42=?
   ↓
OCR
   ↓
21+42
   ↓
Math Solver
   ↓
63
```

The resulting answer is entered into the CAPTCHA field before submission.

---

## 3. Text Question CAPTCHA

Demo:

```text
https://2captcha.com/demo/text
```

Example challenge encountered during development:

```text
If tomorrow is Saturday, what day is today?
```

Expected answer:

```text
Friday
```

The text CAPTCHA workflow is designed for supported text-question cases.

---

## 4. Noisy Image CAPTCHA

Demo:

```text
http://democaptcha.com/demo-form-eng/image.html
```

This CAPTCHA contains additional visual noise and is more difficult for OCR.

During development, a successful OCR result was obtained:

```text
Maaike695
```

The recognition was achieved using multiple image preprocessing variants and OCR candidate ranking.

Because CAPTCHA content is dynamically generated, the exact text will differ between executions.

---

# Page Analyzer

The page analyzer is implemented in:

```text
browser/page_analyzer.py
```

The goal of the page analyzer is to make the system more flexible across different demo webpages.

Instead of relying exclusively on one hard-coded selector, the analyzer searches for likely CAPTCHA-related elements.

---

## CAPTCHA Input Detection

The analyzer searches visible input elements for attributes and terms related to CAPTCHA.

Examples include:

```text
captcha
verification
verify
vericode
code
```

Relevant attributes can include:

```text
id
name
placeholder
aria-label
```

The analyzer prioritizes visible fields that are likely to represent CAPTCHA input.

---

## CAPTCHA Image Detection

The analyzer searches for visual CAPTCHA candidates from:

```html
<img>
<canvas>
<svg>
```

It can also inspect elements containing background images.

Potential candidates are scored using signals such as:

- Visibility
- Image dimensions
- Proximity to CAPTCHA input
- CAPTCHA-related attributes
- Element characteristics

This prevents unrelated images, such as logos or decorative graphics, from being selected when a more relevant CAPTCHA image exists.

---

## Submit Button Detection

The analyzer searches for likely submission controls using common labels such as:

```text
Verify
Check
Submit
Send
Continue
Validate
Confirm
```

It can also inspect input elements with submit behavior.

---

# CAPTCHA Detection

The detector is implemented in:

```text
detector/captcha_detector.py
```

The detector currently supports three classifications:

```text
TEXT
MATH
UNKNOWN
```

---

## Mathematical CAPTCHA Detection

Mathematical expressions are detected using patterns similar to:

```text
21+42
50-17
8*7
64/8
```

The detector also supports common multiplication representations:

```text
8X7
8x7
8×7
```

These can be normalized to:

```text
8*7
```

---

## Text CAPTCHA Detection

Text candidates are evaluated using characteristics such as:

- Character length
- Alphabetic characters
- Numeric characters
- Alphanumeric composition

Examples:

```text
W9H5K
Maaike695
```

can be classified as text CAPTCHA candidates.

---

## Unknown CAPTCHA

If the OCR output does not provide enough information to confidently classify the CAPTCHA, the detector returns:

```text
UNKNOWN
```

This prevents unsupported CAPTCHA formats from automatically being treated as text or mathematical challenges.

---

# OCR Pipeline

The main OCR implementation is located in:

```text
solver/paddle_solver.py
```

The OCR pipeline combines:

```text
PaddleOCR
+
EasyOCR
```

and applies both engines to multiple image variants.

The objective is to reduce dependence on a single OCR prediction.

---

## PaddleOCR

PaddleOCR is the primary OCR engine.

The current implementation uses a text recognition model and processes multiple preprocessed CAPTCHA images.

For each candidate, information such as the following can be considered:

- Recognized text
- OCR confidence
- Image variant
- Number of occurrences

---

## EasyOCR

EasyOCR is used as a secondary OCR engine.

Its results provide another independent recognition signal.

For example:

```text
PaddleOCR → W9H5K
EasyOCR   → W9H5K
```

This agreement provides stronger evidence than a result produced by only one OCR engine.

---

# Image Preprocessing

CAPTCHA images can contain noise, distortion, low contrast, and colored interference.

To improve OCR robustness, the project generates several image variants.

---

## Original

The original CAPTCHA image is passed directly to OCR.

```text
Original
   ↓
OCR
```

This provides the baseline recognition result.

---

## Grayscale

The image is converted from color into grayscale.

```text
RGB
 ↓
Grayscale
 ↓
OCR
```

This removes color information and can simplify character recognition.

---

## Contrast Enhancement

Contrast is enhanced to increase the visual separation between characters and background.

```text
Original
   ↓
Contrast Enhancement
   ↓
OCR
```

---

## Otsu Threshold

Otsu thresholding converts the grayscale image into a binary representation.

```text
Grayscale
    ↓
Otsu Threshold
    ↓
OCR
```

---

## Inverted Otsu

The Otsu result can be inverted.

```text
Otsu
 ↓
Invert
 ↓
OCR
```

This provides an alternative representation when character and background intensity relationships differ.

---

## Adaptive Threshold

Adaptive thresholding calculates local thresholds rather than applying one global threshold.

```text
Grayscale
    ↓
Adaptive Threshold
    ↓
OCR
```

This can be useful for CAPTCHA images with uneven backgrounds.

---

## Sharpening

Sharpening emphasizes edges and character boundaries.

```text
Original
   ↓
Sharpen
   ↓
OCR
```

---

## Saturation Mask

A saturation-based mask is generated as another OCR input.

This can help isolate colored regions in CAPTCHA images where color differences exist between characters and background.

---

## Blue Mask

A blue-channel/color-based mask provides another representation for OCR.

This is particularly useful for experimenting with CAPTCHA images containing blue-colored elements.

---

# OCR Candidate Ranking

A major component of the project is the OCR candidate ranking system.

The system does not simply use the first OCR result.

Instead:

```text
Multiple Image Variants
        +
Multiple OCR Engines
        ↓
Multiple OCR Results
        ↓
Candidate Normalization
        ↓
Candidate Grouping
        ↓
Candidate Scoring
        ↓
Best Candidate
```

---

## Candidate Normalization

OCR outputs are normalized before comparison.

Examples include:

```text
Whitespace removal
Character normalization
Multiplication symbol normalization
Invalid character removal
```

Mathematical symbols are preserved when relevant:

```text
+
-
*
/
=
?
```

This is important because removing mathematical operators can incorrectly transform:

```text
21+42=?
```

into:

```text
2142
```

which makes mathematical CAPTCHA detection more difficult.

---

## Candidate Voting

If multiple OCR runs produce the same candidate, the candidate receives additional support.

Example:

```text
Original       → W9H5K
Gray           → W9H5K
Contrast       → W9H5K
Otsu           → W9H5K
Sharpen        → W9H5K
```

The candidate:

```text
W9H5K
```

has strong variant agreement.

---

## OCR Engine Agreement

Candidates recognized by multiple OCR engines receive additional support.

Example:

```text
PaddleOCR → W9H5K
EasyOCR   → W9H5K
```

This provides a multi-engine agreement signal.

---

## Confidence

OCR confidence is also considered.

Higher confidence contributes positively to the candidate score.

However, confidence is not treated as the only decision factor because an OCR engine can sometimes be highly confident about an incorrect result.

---

## Candidate Shape

The candidate shape is evaluated according to the expected CAPTCHA type.

For example:

```text
21+42
```

has a recognizable mathematical structure.

A noisy result such as:

```text
21427
```

may contain a similar number of characters but does not provide the same mathematical structure.

---

## Mathematical Candidate Scoring

Mathematical candidates receive additional support when they match a valid expression pattern.

For example:

```text
21+42
50-17
8*7
64/8
```

This helps prevent numeric noise from outranking a structurally valid mathematical expression.

---

# CAPTCHA Solvers

Solver implementations are located under:

```text
solver/
```

Current solver modules:

```text
solver/
├── paddle_solver.py
├── math_solver.py
└── text_solver.py
```

---

# Mathematical Solver

The mathematical solver is implemented in:

```text
solver/math_solver.py
```

Example:

```python
solve_math_expression("21+42")
```

Output:

```text
63
```

Supported operators:

```text
+
-
*
/
```

The solver also normalizes:

```text
X
x
×
```

to:

```text
*
```

For example:

```text
8×7
```

is interpreted as:

```text
8*7
```

and produces:

```text
56
```

Division by zero is rejected.

---

# Text Solver

The text solver is implemented in:

```text
solver/text_solver.py
```

It is intended for supported text-based CAPTCHA recognition and text-question cases.

The current implementation is experimental and should not be considered a general natural-language reasoning system.

---

# Form Interaction

Form interaction is implemented in:

```text
interaction/form_handler.py
```

The form handler separates normal form fields from the CAPTCHA field.

For example:

```text
Name
Email
Message
CAPTCHA
```

The system can populate the normal fields first and process the CAPTCHA separately.

---

## CAPTCHA Field Handling

The CAPTCHA input is filled only after the recognition and solving pipeline is completed:

```text
CAPTCHA Image
      ↓
OCR
      ↓
Candidate Ranking
      ↓
CAPTCHA Detection
      ↓
Solver
      ↓
Answer
      ↓
CAPTCHA Input
```

This prevents the CAPTCHA input from being treated as a normal form field.

---

## Required Form Fields

Some demonstration forms contain required fields in addition to the CAPTCHA.

For controlled testing, the form handler can fill empty visible text fields and textareas with test content.

Example:

```text
Automated form testing
```

This content is only intended for demo/testing environments.

---

# Submission Result Detection

After the form is submitted, the system attempts to determine whether the submission was successful.

Success indicators can include messages such as:

```text
Captcha is passed
Success
Successfully
Thank you
Message has been sent
Correct captcha
Verification successful
Verified successfully
```

Failure indicators are checked first to prevent a failure message from being interpreted as success.

Examples include:

```text
Incorrect captcha
Wrong captcha
Captcha failed
Invalid captcha
Try again
Verification failed
```

The final result is recorded as:

```text
SUCCESS
```

or:

```text
FAILED
```

---

# Evaluation and Metrics

Evaluation is implemented in:

```text
evaluation/metrics.py
```

The result file is stored at:

```text
outputs/logs/results.csv
```

The CSV contains:

```text
timestamp
url
captcha_type
ocr_result
answer
result
processing_time_seconds
```

---

## Example CSV

```csv
timestamp,url,captcha_type,ocr_result,answer,result,processing_time_seconds
2026-10-14T10:30:12,http://example-demo.com,math,21+42,63,SUCCESS,12.421
```

---

## Metrics Purpose

The collected results can be used to analyze:

- CAPTCHA recognition performance
- OCR results
- CAPTCHA classification
- Solver correctness
- Submission success rate
- Processing time
- Performance differences between CAPTCHA types
- Effectiveness of different preprocessing strategies

The CSV can later be analyzed using:

- Python
- Pandas
- Microsoft Excel
- Google Sheets
- Other data analysis tools

---

# Debug Output

Debug files are stored under:

```text
outputs/captcha_images/
```

The directory contains:

```text
outputs/
└── captcha_images/
    ├── debug/
    └── ocr_temp/
```

---

## Debug Images

The following preprocessing variants can be stored:

```text
original.png
gray.png
contrast.png
otsu.png
otsu_inverted.png
adaptive.png
sharpen.png
saturation_mask.png
blue_mask.png
```

These images can be inspected manually to determine which preprocessing technique produces the clearest character representation.

---

## OCR Temporary Files

Temporary OCR variants are stored under:

```text
outputs/captcha_images/ocr_temp/
```

These files are useful when debugging OCR recognition problems.

---

# Testing

The project includes basic tests for the page analyzer and CAPTCHA detector.

---

## Page Analyzer Test

Run:

```powershell
python test_analyzer.py
```

This verifies whether the analyzer can identify relevant elements such as:

```text
CAPTCHA input
CAPTCHA image
Submit button
```

The analyzer was tested against the supported demonstration pages during development.

---

## CAPTCHA Detector Test

Run:

```powershell
python test_detector.py
```

The detector test verifies:

```text
TEXT
MATH
UNKNOWN
```

classification.

---

# Example Execution

After activating the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

run:

```powershell
python main.py
```

Example:

```text
========================================
CAPTCHA BOT WEBSITE
========================================

Enter website URL:
> http://democaptcha.com/demo-form-eng/math-image.html
```

The system then analyzes the webpage.

Example:

```text
Analyzing page...

CAPTCHA input detected
CAPTCHA image detected
Submit button detected
```

The CAPTCHA image is captured and passed through the OCR pipeline.

---

# Example OCR Candidate Ranking

For a mathematical CAPTCHA, the OCR pipeline may produce multiple candidates.

Example:

```text
OCR CANDIDATE RANKING

1. 21+42=?
   score=...
   votes=...
   confidence=...
   shape=...
   engines: paddle, easyocr
   variants: original, gray, otsu, sharpen

2. 21427
   score=...
   votes=...
   confidence=...
   shape=...
   engines: paddle
   variants: blue_mask, gray

3. 214427
   score=...
   votes=...
   confidence=...
   shape=...
```

The candidate with the highest final score is selected.

For a mathematical CAPTCHA:

```text
21+42=?
```

is then passed to the mathematical solver.

---

# Example End-to-End Result

Example workflow:

```text
CAPTCHA type:
math

OCR:
21+42=?

Answer:
63

Submitting form...

Result:
SUCCESS
```

For a text CAPTCHA:

```text
CAPTCHA type:
text

OCR:
W9H5K

Answer:
W9H5K

Submitting form...

Result:
SUCCESS
```

For a noisy image CAPTCHA:

```text
CAPTCHA type:
text

OCR:
Maaike695

Answer:
Maaike695

Submitting form...

Result:
SUCCESS
```

The exact output depends on the CAPTCHA generated by the demo environment.

---

# Experimental Results

During development, several demo CAPTCHA types were successfully processed.

| CAPTCHA Type | Demo Environment | OCR Approach | Result |
|---|---|---|---|
| Normal Text | 2Captcha Demo | PaddleOCR | Successful recognition |
| Mathematical | DemoCaptcha | OCR + Math Solver | Successful |
| Text Question | 2Captcha Demo | Text processing | Successful |
| Noisy Image | DemoCaptcha | Multi-variant OCR | Successful |

These results demonstrate that the pipeline can process several controlled CAPTCHA examples.

However, these results should not be interpreted as a universal CAPTCHA-solving accuracy benchmark because:

- CAPTCHA content changes dynamically.
- CAPTCHA providers use different image-generation methods.
- The number of tested examples is limited.
- Different CAPTCHA configurations can produce significantly different OCR difficulty.
- Demo environments may change over time.

A larger benchmark is required to make statistically meaningful performance claims.

---

# Performance Considerations

The multi-variant OCR pipeline improves robustness but increases processing time.

A single CAPTCHA image may be processed using:

```text
9 image variants
        ×
2 OCR engines
        =
18 OCR processing operations
```

Therefore, the system may take significantly longer than a single-pass OCR implementation.

The trade-off can be summarized as:

```text
Single OCR
    ↓
Lower processing time
    ↓
Potentially lower robustness

Multi-variant + Multi-engine OCR
    ↓
Higher processing time
    ↓
More recognition candidates
    ↓
Potentially higher robustness
```

This trade-off should be considered when optimizing the system for future experiments.

---

# Current Limitations

The current implementation has several limitations.

## 1. OCR Dependence

Recognition quality strongly depends on the CAPTCHA image itself.

Highly distorted or heavily noisy images can still produce incorrect OCR results.

---

## 2. Dynamic Website Structure

Different websites use different:

- HTML structures
- Input attributes
- CAPTCHA layouts
- Button labels
- Success messages

Therefore, the page analyzer cannot guarantee compatibility with every website.

---

## 3. CAPTCHA Type Coverage

The current detector mainly supports:

```text
Text CAPTCHA
Mathematical CAPTCHA
```

Other CAPTCHA formats are outside the current scope.

---

## 4. Text Question Handling

Text-question CAPTCHA support is currently limited to supported cases.

It is not a general-purpose question-answering engine.

---

## 5. OCR False Positives

A high OCR confidence score does not necessarily mean that the result is correct.

For example:

```text
Expected:
21+42

Possible OCR:
21427
```

The OCR engine may still assign a relatively high confidence to an incorrect recognition.

This is one reason why candidate ranking uses multiple signals.

---

## 6. Processing Time

Running multiple preprocessing variants through multiple OCR engines increases computation time.

This is especially noticeable when using:

```text
PaddleOCR
+
EasyOCR
+
Multiple Image Variants
```

---

## 7. No Universal CAPTCHA Support

The project is designed around controlled demonstration and testing environments.

It should not be considered a universal CAPTCHA-solving system.

---

# Future Improvements

Several improvements can be explored in future versions.

## CAPTCHA Detection

- More robust CAPTCHA element detection
- Better visual CAPTCHA classification
- Improved detection of CAPTCHA containers
- More reliable relationship analysis between input and image

---

## OCR

- Better OCR model selection
- Additional OCR engines
- Automatic OCR engine selection
- Confidence calibration
- OCR ensemble techniques
- Character-level voting

---

## Image Processing

- Automatic preprocessing selection
- CAPTCHA-specific preprocessing pipelines
- Perspective correction
- Noise estimation
- Automatic threshold selection
- Morphological filtering
- Character segmentation

---

## Candidate Ranking

Future ranking improvements could include:

- More sophisticated confidence calibration
- Character-level consensus
- Edit-distance-based candidate grouping
- CAPTCHA-type-specific scoring
- Learned candidate ranking
- Historical evaluation-based weighting

---

## Evaluation

Future experiments could measure:

```text
OCR Accuracy
CAPTCHA Classification Accuracy
Solver Accuracy
Submission Success Rate
Average Processing Time
Median Processing Time
Failure Rate
```

Additional comparisons could include:

```text
PaddleOCR only
EasyOCR only
PaddleOCR + preprocessing
EasyOCR + preprocessing
PaddleOCR + EasyOCR
PaddleOCR + EasyOCR + candidate ranking
```

This would provide a more systematic evaluation of the contribution of each component.

---

# Recommended Experiment Design

For a more rigorous evaluation, the project can be extended with a fixed CAPTCHA benchmark.

For example:

```text
Dataset
   │
   ├── Easy CAPTCHA
   ├── Medium CAPTCHA
   └── Noisy CAPTCHA
```

Each CAPTCHA can be evaluated using:

```text
Method A: Original + PaddleOCR
Method B: Preprocessing + PaddleOCR
Method C: Preprocessing + EasyOCR
Method D: Multi-engine OCR
Method E: Multi-engine + Candidate Ranking
```

The resulting metrics can then be compared.

Example table:

| Method | Accuracy | Avg. Time | Failure Rate |
|---|---:|---:|---:|
| PaddleOCR | - | - | - |
| EasyOCR | - | - | - |
| PaddleOCR + Preprocessing | - | - | - |
| Multi-Engine OCR | - | - | - |
| Multi-Engine + Ranking | - | - | - |

The values should be populated only after running a controlled benchmark.

---

# Ethical and Legal Considerations

CAPTCHA exists primarily as an anti-automation and abuse-prevention mechanism.

Therefore, any automated CAPTCHA research should be performed within an authorized environment.

Appropriate environments include:

- Personal test websites
- Local development environments
- Controlled staging environments
- Public CAPTCHA demonstration pages
- Security research with explicit authorization
- Educational experiments

The project should not be used to:

- Bypass CAPTCHA on third-party websites without permission
- Circumvent anti-bot protections
- Automate unauthorized account creation
- Circumvent rate limits
- Circumvent access controls
- Conduct automated abuse against third-party services

The purpose of this repository is to study OCR, computer vision, browser automation, and evaluation techniques in controlled environments.

---

# Development Environment

The project was developed and tested using:

```text
Operating System:
Windows

IDE:
Visual Studio Code

Python:
3.10+

Browser Automation:
Playwright

OCR:
PaddleOCR
EasyOCR

Image Processing:
OpenCV

Deep Learning:
PaddlePaddle
PyTorch
```

---

# Quick Start

For future runs, the complete process is:

```powershell
cd "C:\Users\ACER\Captcha Bot Website"
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If required:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python main.py
```

Then enter an authorized CAPTCHA demo URL.

---

# Troubleshooting

## PowerShell Execution Policy Error

If you see an error related to script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Playwright Browser Not Found

Install Chromium:

```powershell
playwright install chromium
```

---

## Python Package Missing

Verify that the virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then reinstall dependencies:

```powershell
pip install -r requirements.txt
```

---

## OCR Result Is Incorrect

Inspect the generated images under:

```text
outputs/captcha_images/debug/
```

Compare:

```text
original
gray
contrast
otsu
otsu_inverted
adaptive
sharpen
saturation_mask
blue_mask
```

Also inspect the printed:

```text
OCR CANDIDATE RANKING
```

to determine whether another candidate received sufficient votes or confidence.

---

## CAPTCHA Type Is Incorrect

Check the OCR output first.

For mathematical CAPTCHA, make sure mathematical operators are preserved:

```text
+
-
*
/
=
?
```

For example:

```text
21+42=?
```

should not be normalized into:

```text
2142
```

because removing the operator prevents reliable mathematical classification.

---

# Repository Status

This project is currently an experimental prototype.

The architecture is intentionally modular so that individual components can be improved independently:

```text
Browser
   ↓
Analyzer
   ↓
Detector
   ↓
OCR
   ↓
Solver
   ↓
Interaction
   ↓
Evaluation
```

This makes it possible to experiment with different OCR engines, preprocessing techniques, CAPTCHA detectors, and ranking strategies without rewriting the entire application.

---

# License

This project is intended for educational, research, and authorized testing purposes.

If this repository is distributed publicly, add an appropriate open-source license here, for example:

```text
MIT License
```

The license should be selected based on the intended distribution and dependencies of the project.

---

## Disclaimer

This repository is provided for educational and authorized testing purposes.

The author does not encourage or endorse unauthorized CAPTCHA bypassing, anti-bot circumvention, or abuse of third-party websites.

Use the software responsibly and only against systems for which you have permission to perform automated testing.
```