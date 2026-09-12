# OCR Book Digitization Application

A web application for digitizing scanned PDF books and documents using Optical Character Recognition (OCR).

The application is developed with Python and Flask. It converts scanned PDF pages into images, preprocesses them using OpenCV, performs OCR with Tesseract, and allows the user to review, search, manually correct, and export the recognized text.

The application is primarily intended for scanned documents written in Macedonian Cyrillic.

---

## Features

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
- Export the corrected document as a `.txt` file
- Detection of mostly blank pages
- Background OCR processing with progress status

---

## Technologies

**Backend**
- Python
- Flask

**OCR and Image Processing**
- Tesseract OCR
- pytesseract
- pdf2image
- Poppler
- OpenCV
- NumPy
- Pillow

**Frontend**
- HTML
- CSS
- JavaScript

---

## Project Structure

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

Both directories are created automatically by the application if they do not already exist.

---

# Installation

The following instructions are intended for Windows.

## 1. Prerequisites

Before running the application, make sure the following software is installed:

- Python 3
- Git
- Tesseract OCR
- Macedonian Tesseract language data (`mkd`)
- Poppler

---

## 2. Clone the Repository

Open Command Prompt or another terminal in the directory where you want to store the project and run:

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

After activation, the terminal should display `(.venv)` before the current directory.

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

Tesseract OCR and Poppler are external system dependencies and are therefore not installed through `requirements.txt`.

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

If Tesseract is installed in another location, use the corresponding path instead.

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

If `mkd` is not available, download the official `mkd.traineddata` Tesseract language file and place it inside the Tesseract `tessdata` directory.

For a standard Windows installation, the directory is usually:

```text
C:\Program Files\Tesseract-OCR\tessdata
```

The final file should look similar to:

```text
C:\Program Files\Tesseract-OCR\tessdata\mkd.traineddata
```

After adding the file, run `--list-langs` again and verify that `mkd` appears.

---

## 7. Configure Tesseract

The application attempts to locate Tesseract automatically.

It also checks the standard Windows installation location:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is installed in another location, set the `TESSERACT_CMD` environment variable before starting the application:

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

Inside the extracted directory, locate the folder that contains files such as:

```text
pdftoppm.exe
pdfinfo.exe
```

Depending on the Poppler distribution, the directory may look similar to:

```text
path\to\poppler\Library\bin
```

The exact location may be different on each computer.

---

## 9. Configure Poppler

If Poppler is already available through the Windows `PATH`, no additional configuration may be required.

Otherwise, set the `POPPLER_PATH` environment variable before starting the application:

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

After the initial installation, open a terminal in the project directory.

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

If the application starts successfully, the terminal should display an address similar to:

```text
http://127.0.0.1:5000
```

Open that address in a web browser.

---

# Typical Startup

After Tesseract, Poppler, and the Python dependencies have already been installed, a typical startup is:

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

### PDF Upload

The user uploads a scanned PDF document through the web interface.

### PDF to Image Conversion

`pdf2image` uses Poppler to convert each page of the PDF into an image.

### Image Preprocessing

Before OCR, each page is processed using Pillow, NumPy, and OpenCV.

The preprocessing includes:

- grayscale conversion
- automatic contrast adjustment
- small border cropping
- resizing of smaller images
- Gaussian blur
- Otsu thresholding

These steps help prepare scanned pages for OCR.

### Blank Page Detection

The application checks whether a processed page contains enough meaningful visual content.

Pages detected as mostly blank do not need full OCR processing.

### OCR Processing

Tesseract processes the prepared page image using the Macedonian language model:

```python
lang="mkd"
```

OCR processing is performed in the background while the application stores the current processing status.

### Review

After processing is completed, the user can view the scanned page together with the extracted text.

### Search

The application allows the user to search the recognized text by word or phrase.

Pages containing the requested text are returned as search results.

### Manual Correction

The user can manually correct OCR errors.

The corrected version is stored separately so that changes can be preserved.

### Export

The corrected text can be downloaded as a UTF-8 `.txt` document.

---

# Notes

- The user interface is in Macedonian.
- The application is primarily designed for scanned Macedonian Cyrillic documents and books.
- The maximum uploaded PDF size is 50 MB.
- Tesseract OCR and Poppler must be installed separately from the Python dependencies.
- The Macedonian Tesseract language model (`mkd`) is required.
- Installation paths for Tesseract and Poppler may differ between computers.
- The project itself can be stored on any available drive or directory.
- Environment variables set with the Windows `set` command apply to the current Command Prompt session and may need to be set again when opening a new terminal.

---

## Author

Developed as an OCR proof-of-concept application for scanned book and document digitization.
