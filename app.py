import os
import uuid
import json
import threading
import shutil

import numpy as np
import cv2

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageOps


app = Flask(__name__)


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")

ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# -------------------------------------------------
# TESSERACT CONFIGURATION
# -------------------------------------------------

# First try environment variable or system PATH
tesseract_cmd = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")

# Standard Windows installation location
if not tesseract_cmd:
    default_windows_tesseract = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if os.path.isfile(default_windows_tesseract):
        tesseract_cmd = default_windows_tesseract


if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


# -------------------------------------------------
# POPPLER CONFIGURATION
# -------------------------------------------------

# If POPPLER_PATH is not set, pdf2image will search
# for Poppler automatically through the system PATH.
POPPLER_PATH = os.getenv("POPPLER_PATH") or None


# -------------------------------------------------
# FILE HELPERS
# -------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_book_folder(book_id):
    return os.path.join(PROCESSED_FOLDER, book_id)


def get_pages_folder(book_id):
    return os.path.join(get_book_folder(book_id), "pages")


def get_status_path(book_id):
    return os.path.join(get_book_folder(book_id), "status.json")


def get_ocr_path(book_id):
    return os.path.join(get_book_folder(book_id), "ocr.json")


def get_corrected_path(book_id):
    return os.path.join(get_book_folder(book_id), "corrected.json")


# -------------------------------------------------
# JSON DATA
# -------------------------------------------------

def save_status(book_id, status_data):
    book_folder = get_book_folder(book_id)

    os.makedirs(book_folder, exist_ok=True)

    with open(
        get_status_path(book_id),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            status_data,
            f,
            ensure_ascii=False,
            indent=2
        )


def load_status(book_id):
    status_path = get_status_path(book_id)

    if not os.path.exists(status_path):
        return None

    with open(
        status_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_corrected_data(book_id):
    corrected_json_path = get_corrected_path(book_id)

    if not os.path.exists(corrected_json_path):
        return None

    with open(
        corrected_json_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_corrected_data(book_id, data):
    with open(
        get_corrected_path(book_id),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# -------------------------------------------------
# IMAGE PREPROCESSING
# -------------------------------------------------

def preprocess_image_for_ocr(image):

    # Convert to grayscale
    gray_pil = image.convert("L")

    # Improve contrast
    gray_pil = ImageOps.autocontrast(gray_pil)

    width, height = gray_pil.size

    # Remove a very small border around the page
    left = int(width * 0.01)
    top = int(height * 0.005)
    right = int(width * 0.99)
    bottom = int(height * 0.995)

    cropped_pil = gray_pil.crop(
        (left, top, right, bottom)
    )

    img = np.array(cropped_pil)

    _, image_width = img.shape

    min_target_width = 1600

    # Enlarge smaller scanned pages
    if image_width < min_target_width:

        scale = min_target_width / image_width

        img = cv2.resize(
            img,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    # Reduce noise
    img = cv2.GaussianBlur(
        img,
        (3, 3),
        0
    )

    # Automatic thresholding
    _, binary = cv2.threshold(
        img,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    processed_pil = Image.fromarray(binary)

    return processed_pil, binary


# -------------------------------------------------
# BLANK PAGE DETECTION
# -------------------------------------------------

def is_page_mostly_blank(binary_img):

    black_ratio = np.mean(
        binary_img == 0
    )

    if black_ratio < 0.003:
        return True

    inverted = 255 - binary_img

    num_labels, _, stats, _ = (
        cv2.connectedComponentsWithStats(
            inverted,
            connectivity=8
        )
    )

    significant_components = 0

    for i in range(1, num_labels):

        area = stats[
            i,
            cv2.CC_STAT_AREA
        ]

        if area >= 25:
            significant_components += 1

    return significant_components < 8


# -------------------------------------------------
# OCR PROCESSING
# -------------------------------------------------

def process_pdf_to_ocr_async(
    upload_path,
    book_id
):

    book_folder = get_book_folder(book_id)
    pages_folder = get_pages_folder(book_id)

    os.makedirs(
        book_folder,
        exist_ok=True
    )

    os.makedirs(
        pages_folder,
        exist_ok=True
    )

    try:

        save_status(
            book_id,
            {
                "status": "processing",
                "message": "Се подготвува OCR обработка...",
                "current_page": 0,
                "total_pages": 0
            }
        )

        # Convert PDF pages to images
        images = convert_from_path(
            upload_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )

        total_pages = len(images)

        save_status(
            book_id,
            {
                "status": "processing",
                "message":
                    "PDF документот е прочитан. "
                    "Започнува OCR обработка...",
                "current_page": 0,
                "total_pages": total_pages
            }
        )

        pages_data = []

        for i, image in enumerate(
            images,
            start=1
        ):

            processed_image, binary_img = (
                preprocess_image_for_ocr(
                    image
                )
            )

            image_filename = (
                f"page_{i:03}.png"
            )

            image_path = os.path.join(
                pages_folder,
                image_filename
            )

            processed_image.save(
                image_path,
                "PNG"
            )

            # Skip mostly blank pages
            if is_page_mostly_blank(
                binary_img
            ):

                text = ""

            else:

                text = (
                    pytesseract.image_to_string(
                        processed_image,
                        lang="mkd"
                    )
                    .strip()
                )

            pages_data.append(
                {
                    "page_number": i,
                    "image": image_filename,
                    "text": text
                }
            )

            save_status(
                book_id,
                {
                    "status":
                        "processing",

                    "message":
                        f"Се обработува страна "
                        f"{i} од {total_pages}...",

                    "current_page":
                        i,

                    "total_pages":
                        total_pages
                }
            )

        ocr_data = {
            "book_id": book_id,
            "total_pages":
                len(pages_data),
            "pages":
                pages_data
        }

        # Save original OCR result
        with open(
            get_ocr_path(book_id),
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                ocr_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        # Save editable copy
        with open(
            get_corrected_path(book_id),
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                ocr_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        save_status(
            book_id,
            {
                "status":
                    "completed",

                "message":
                    "OCR обработката е успешно завршена.",

                "current_page":
                    total_pages,

                "total_pages":
                    total_pages
            }
        )

    except Exception as e:

        save_status(
            book_id,
            {
                "status":
                    "error",

                "message":
                    f"Грешка при OCR обработка: {str(e)}",

                "current_page":
                    0,

                "total_pages":
                    0
            }
        )


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html",
        active_page="instructions"
    )


# -------------------------------------------------
# WORKSPACE
# -------------------------------------------------

@app.route("/workspace")
def workspace():

    return render_template(
        "workspace.html",
        active_page="workspace"
    )


# -------------------------------------------------
# UPLOAD PDF
# -------------------------------------------------

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    if "file" not in request.files:

        return jsonify(
            {
                "success": False,
                "message":
                    "Недостасува PDF фајлот."
            }
        ), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify(
            {
                "success": False,
                "message":
                    "Не е избран фајл."
            }
        ), 400


    if not allowed_file(
        file.filename
    ):

        return jsonify(
            {
                "success": False,
                "message":
                    "Дозволени се само PDF фајлови."
            }
        ), 400


    filename = secure_filename(
        file.filename
    )

    book_id = str(
        uuid.uuid4()
    )


    book_folder = get_book_folder(
        book_id
    )

    os.makedirs(
        book_folder,
        exist_ok=True
    )


    upload_path = os.path.join(
        app.config[
            "UPLOAD_FOLDER"
        ],
        f"{book_id}_{filename}"
    )


    file.save(
        upload_path
    )


    save_status(
        book_id,
        {
            "status":
                "queued",

            "message":
                "Документот е прикачен. "
                "Обработката ќе започне веднаш.",

            "current_page":
                0,

            "total_pages":
                0
        }
    )


    worker = threading.Thread(
        target=process_pdf_to_ocr_async,
        args=(
            upload_path,
            book_id
        ),
        daemon=True
    )


    worker.start()


    return jsonify(
        {
            "success":
                True,

            "message":
                "Документот е успешно прикачен. "
                "OCR обработката е започната.",

            "book_id":
                book_id
        }
    )


# -------------------------------------------------
# OCR STATUS
# -------------------------------------------------

@app.route(
    "/status/<book_id>",
    methods=["GET"]
)
def check_status(book_id):

    status_data = load_status(
        book_id
    )


    if not status_data:

        return jsonify(
            {
                "success": False,
                "message":
                    "Книгата не е пронајдена."
            }
        ), 404


    return jsonify(
        {
            "success":
                True,

            "book_id":
                book_id,

            "status":
                status_data.get(
                    "status"
                ),

            "message":
                status_data.get(
                    "message"
                ),

            "current_page":
                status_data.get(
                    "current_page",
                    0
                ),

            "total_pages":
                status_data.get(
                    "total_pages",
                    0
                )
        }
    )


# -------------------------------------------------
# GET PAGE
# -------------------------------------------------

@app.route(
    "/book/<book_id>/page/<int:page_number>",
    methods=["GET"]
)
def get_page(
    book_id,
    page_number
):

    data = load_corrected_data(
        book_id
    )


    if not data:

        return jsonify(
            {
                "success": False,

                "message":
                    "Книгата не е пронајдена "
                    "или обработката не е завршена."
            }
        ), 404


    if (
        page_number < 1
        or
        page_number > data[
            "total_pages"
        ]
    ):

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Невалиден број на страна."
            }
        ), 400


    page_data = data[
        "pages"
    ][
        page_number - 1
    ]


    return jsonify(
        {
            "success":
                True,

            "book_id":
                book_id,

            "page_number":
                page_data[
                    "page_number"
                ],

            "total_pages":
                data[
                    "total_pages"
                ],

            "text":
                page_data[
                    "text"
                ],

            "image_url":
                f"/page-image/"
                f"{book_id}/"
                f"{page_data['image']}"
        }
    )


# -------------------------------------------------
# SEARCH
# -------------------------------------------------

@app.route(
    "/search/<book_id>"
)
def search_book(book_id):

    query = request.args.get(
        "q",
        ""
    ).strip()


    if not query:

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Внеси збор за пребарување."
            }
        ), 400


    data = load_corrected_data(
        book_id
    )


    if not data:

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Книгата не е пронајдена "
                    "или обработката не е завршена."
            }
        ), 404


    results = []

    query_lower = query.lower()


    for page in data["pages"]:

        page_text = page.get(
            "text",
            ""
        )


        if (
            query_lower
            in
            page_text.lower()
        ):

            snippet = (
                page_text
                .replace(
                    "\n",
                    " "
                )
                .strip()
            )


            if len(snippet) > 220:

                snippet = (
                    snippet[:220]
                    + "..."
                )


            results.append(
                {
                    "page_number":
                        page[
                            "page_number"
                        ],

                    "snippet":
                        snippet
                }
            )


    return jsonify(
        {
            "success":
                True,

            "query":
                query,

            "count":
                len(results),

            "results":
                results
        }
    )


# -------------------------------------------------
# PAGE IMAGE
# -------------------------------------------------

@app.route(
    "/page-image/<book_id>/<filename>"
)
def page_image(
    book_id,
    filename
):

    pages_folder = (
        get_pages_folder(
            book_id
        )
    )

    return send_from_directory(
        pages_folder,
        filename
    )


# -------------------------------------------------
# SAVE CORRECTION
# -------------------------------------------------

@app.route(
    "/save-correction",
    methods=["POST"]
)
def save_correction():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    book_id = data.get(
        "book_id"
    )

    page_number = data.get(
        "page_number"
    )

    corrected_text = data.get(
        "text",
        ""
    )


    if (
        not book_id
        or
        not page_number
    ):

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Недостасуваат податоци."
            }
        ), 400


    book_data = (
        load_corrected_data(
            book_id
        )
    )


    if not book_data:

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Книгата не е пронајдена."
            }
        ), 404


    if (
        page_number < 1
        or
        page_number
        >
        book_data[
            "total_pages"
        ]
    ):

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Невалиден број на страна."
            }
        ), 400


    book_data[
        "pages"
    ][
        page_number - 1
    ][
        "text"
    ] = corrected_text


    save_corrected_data(
        book_id,
        book_data
    )


    return jsonify(
        {
            "success":
                True,

            "message":
                "Корекцијата е успешно зачувана."
        }
    )


# -------------------------------------------------
# DOWNLOAD TXT
# -------------------------------------------------

@app.route(
    "/download/<book_id>"
)
def download_book(book_id):

    data = load_corrected_data(
        book_id
    )


    if not data:

        return jsonify(
            {
                "success":
                    False,

                "message":
                    "Книгата не е пронајдена."
            }
        ), 404


    book_folder = get_book_folder(
        book_id
    )


    export_path = os.path.join(
        book_folder,
        "corrected_book.txt"
    )


    with open(
        export_path,
        "w",
        encoding="utf-8"
    ) as f:

        for page in data["pages"]:

            f.write(
                f"===== Страна "
                f"{page['page_number']} "
                f"=====\n\n"
            )

            f.write(
                page.get(
                    "text",
                    ""
                )
            )

            f.write(
                "\n\n"
            )


    return send_from_directory(
        book_folder,
        "corrected_book.txt",
        as_attachment=True
    )


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=False)
