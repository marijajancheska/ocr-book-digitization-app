# OCR Web Application for Book Digitization

This project is a web-based OCR application for digitizing scanned PDF books and documents.

The user uploads a PDF file, the system performs OCR processing, and then allows:
- page-by-page viewing
- navigation through pages
- search by word or phrase
- manual correction of OCR text
- download of the corrected text as a `.txt` file

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Tesseract OCR
- pytesseract
- pdf2image
- Poppler

## How It Works

1. The user uploads a scanned PDF document.
2. The backend converts the PDF into images.
3. OCR is performed on each page.
4. The extracted text is stored page by page.
5. The user can browse pages, search text, correct OCR mistakes, and download the final corrected text.

## Main Features

- PDF upload
- OCR processing
- Page navigation
- Search functionality
- OCR text correction
- TXT export of corrected text

## Project Structure

- `app.py` - Flask backend
- `templates/` - HTML pages
- `static/` - CSS and JavaScript files

## Notes

- The user interface of the application is in Macedonian.
- The application is primarily intended for scanned books and documents written in Macedonian Cyrillic.
- The project was developed as part of a book digitization and OCR workflow.