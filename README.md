# OCR Book Digitization Application

A web application for digitizing scanned PDF books and documents using Optical Character Recognition (OCR).

The application is developed with Python and Flask. It converts scanned PDF pages into images, preprocesses them using OpenCV, performs OCR with Tesseract, and allows the user to review, search, manually correct, and export the recognized text.

The application is primarily intended for scanned documents written in Macedonian Cyrillic.

---

# Quick Start

For Windows:

1. Clone the repository:

```cmd
git clone https://github.com/marijajancheska/ocr-book-digitization-app.git
cd ocr-book-digitization-app
```

2. Create and activate a virtual environment:

```cmd
py -m venv .venv
.venv\Scripts\activate
```

3. Install the Python dependencies:

```cmd
pip install -r requirements.txt
```

4. Install:
   - Tesseract OCR
   - Macedonian Tesseract language data (`mkd`)
   - Poppler

5. If Tesseract and Poppler are not available through the system `PATH`, configure their locations:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
set POPPLER_PATH=path\to\poppler\Library\bin
```

6. Start the application:

```cmd
python app.py
```

7. Open in a browser:

```text
http://127.0.0.1:5000
```

Detailed installation instructions are provided below.

---

# Features

- Upload scanned PDF documents
- Convert PDF pages to images
- Image preprocessing before OCR
- OCR processing with Tesseract
- Macedonian Cyrillic OCR support
- Page-by-page document preview
- Navigation through processed pages
- Search by word or phrase
- Manual correction of OCR text
- Save corrected OCR text
- Export corrected text as a `.txt` file
- Detection of mostly blank pages
- Background OCR processing with progress status

---

# Technologies

## Backend

- Python
- Flask

## OCR and Image Processing

- Tesseract OCR
- pytesseract
- pdf2image
- Poppler
- OpenCV
- NumPy
- Pillow

## Frontend

- HTML
- CSS
- JavaScript

---

# Project Structure

```text
ocr-book-digitization-app/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   └── workspace.html
│
├── static/
│   ├── css/
│   └── js/
│
├── uploads/
└── processed/
```

The `uploads/` directory is used for temporarily storing uploaded PDF files.

The `processed/` directory stores generated page images, OCR results, corrected text, and processing status information.

These directories are created automatically by the application if they do not already exist.

---

# Installation

The following instructions are intended for Windows.

## 1. Prerequisites

Before running the application, make sure the following software is available:

- Python 3
- Git
- Tesseract OCR
- Macedonian Tesseract language data (`mkd`)
- Poppler

Tesseract and Poppler are external system dependencies and are not installed through `requirements.txt`.

---

## 2. Clone the Repository

Open Command Prompt or another terminal in the directory where you want to store the project:

```cmd
git clone https://github.com/marijajancheska/ocr-book-digitization-app.git
cd ocr-book-digitization-app
```

The project can be stored on any available drive or directory.

---

## 3. Create a Virtual Environment

Create a Python virtual environment:

```cmd
py -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

After activation, the terminal should show `(.venv)` before the current directory.

Example:

```text
(.venv) ...\ocr-book-digitization-app>
```

---

## 4. Install Python Dependencies

Install the required Python packages:

```cmd
pip install -r requirements.txt
```

The project uses:

```text
Flask
pytesseract
pdf2image
Pillow
numpy
opencv-python
```

---

# Tesseract OCR Setup

## 5. Install Tesseract OCR

Tesseract OCR must be installed separately.

One option on Windows is:

```cmd
winget install -e --id UB-Mannheim.TesseractOCR
```

A common installation location is:

```text
C:\Program Files\Tesseract-OCR
```

Verify the installation:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

If Tesseract is installed in another location, use the appropriate path instead.

---

## 6. Macedonian Language Support

The application performs OCR using the Macedonian language model:

```python
lang="mkd"
```

Check the installed Tesseract languages:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

The output must include:

```text
mkd
```

If `mkd` is not available, download the official Tesseract Macedonian language file:

```text
mkd.traineddata
```

and place it inside the Tesseract `tessdata` directory.

For a standard Windows installation, this directory is usually:

```text
C:\Program Files\Tesseract-OCR\tessdata
```

The final file should therefore be located at:

```text
C:\Program Files\Tesseract-OCR\tessdata\mkd.traineddata
```

After adding the file, verify again:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

and confirm that `mkd` is listed.

---

## 7. Configure Tesseract

The application attempts to locate Tesseract automatically.

It checks:

1. the `TESSERACT_CMD` environment variable
2. Tesseract available through the system `PATH`
3. the common Windows location:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is installed somewhere else, set its location before starting the application:

```cmd
set TESSERACT_CMD=path\to\tesseract.exe
```

Example:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

# Poppler Setup

## 8. Install Poppler

Poppler is required by `pdf2image` to convert PDF pages into images.

Download and extract a Windows build of Poppler.

Inside the extracted Poppler directory, locate the folder that contains files such as:

```text
pdftoppm.exe
pdfinfo.exe
```

Depending on the Poppler distribution, the directory may look similar to:

```text
path\to\poppler\Library\bin
```

The exact path may be different on each computer.

---

## 9. Configure Poppler

If Poppler is already available through the system `PATH`, no additional configuration may be required.

Otherwise, set the `POPPLER_PATH` environment variable:

```cmd
set POPPLER_PATH=path\to\poppler\Library\bin
```

Example:

```cmd
set POPPLER_PATH=D:\Tools\poppler\Library\bin
```

Use the actual Poppler location on the computer.

---

# Running the Application

Open a terminal in the project directory.

Activate the virtual environment:

```cmd
.venv\Scripts\activate
```

If necessary, configure Tesseract:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Poppler is not available through the system `PATH`, configure its location:

```cmd
set POPPLER_PATH=path\to\poppler\Library\bin
```

Start the Flask application:

```cmd
python app.py
```

If the application starts successfully, the terminal should display something similar to:

```text
Running on http://127.0.0.1:5000
```

Open the following address in a web browser:

```text
http://127.0.0.1:5000
```

---

# Typical Startup After Initial Installation

After Tesseract, Poppler, the Macedonian language model, and the Python dependencies have already been installed, a typical startup is:

```cmd
cd path\to\ocr-book-digitization-app

.venv\Scripts\activate

set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

set POPPLER_PATH=path\to\poppler\Library\bin

python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

If Tesseract and Poppler are already available through the system `PATH`, the corresponding environment variable commands may not be necessary.

---

# How the Application Works

```text
Scanned PDF
     ↓
PDF to image conversion
     ↓
Image preprocessing
     ↓
Tesseract OCR
     ↓
Extracted text
     ↓
Review and navigation
     ↓
Search and manual correction
     ↓
TXT export
```

## 1. PDF Upload

The user uploads a scanned PDF document through the web interface.

## 2. PDF to Image Conversion

`pdf2image` uses Poppler to convert each page of the PDF into an image.

## 3. Image Preprocessing

Before OCR, each page is processed using Pillow, NumPy, and OpenCV.

The preprocessing includes:

- grayscale conversion
- automatic contrast adjustment
- small border cropping
- resizing of smaller images
- Gaussian blur
- Otsu thresholding

These steps prepare the scanned page for OCR processing.

## 4. Blank Page Detection

The application checks whether a processed page contains enough meaningful visual content.

Pages detected as mostly blank can be skipped during OCR processing.

## 5. OCR Processing

Tesseract processes the prepared page image using the Macedonian language model:

```python
lang="mkd"
```

OCR processing runs in the background while the application stores the current processing status.

## 6. Review and Navigation

After processing is completed, the user can view the processed page together with the extracted text and navigate between pages.

## 7. Search

The application allows searching for a word or phrase inside the recognized text.

Matching pages are returned as search results.

## 8. Manual Correction

The user can manually correct OCR errors.

The corrected text is saved separately from the original OCR result.

## 9. Export

The corrected document can be downloaded as a UTF-8 `.txt` file.

---

# Troubleshooting

## Tesseract is not found

If the application cannot find Tesseract, verify the installation:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

Then set:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## Macedonian OCR language is missing

Check:

```cmd
"C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

Make sure the output contains:

```text
mkd
```

If it does not, add `mkd.traineddata` to the Tesseract `tessdata` directory.

---

## PDF page count / Poppler error

If an error similar to the following appears:

```text
Unable to get page count. Is poppler installed and in PATH?
```

verify that the Poppler directory contains:

```text
pdftoppm.exe
pdfinfo.exe
```

Then set:

```cmd
set POPPLER_PATH=path\to\poppler\Library\bin
```

and restart the application.

---

# Notes

- The user interface is in Macedonian.
- The application is primarily designed for scanned Macedonian Cyrillic books and documents.
- The maximum uploaded PDF size is 50 MB.
- Tesseract OCR and Poppler must be installed separately from the Python dependencies.
- The Macedonian Tesseract language model (`mkd`) is required.
- Installation paths for Tesseract and Poppler may differ between computers.
- The project itself can be stored on any available drive or directory.
- Environment variables set using the Windows `set` command apply to the current Command Prompt session and may need to be set again after opening a new terminal.

---

## Author

Developed as an OCR proof-of-concept application for scanned book and document digitization.
