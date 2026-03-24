document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("uploadForm");
    if (!uploadForm) return;

    const uploadBtn = document.getElementById("uploadBtn");
    const fileInput = document.getElementById("fileInput");
    const statusMessage = document.getElementById("statusMessage");

    const viewerSection = document.getElementById("viewerSection");
    const pageInfo = document.getElementById("pageInfo");
    const pageImage = document.getElementById("pageImage");
    const pageText = document.getElementById("pageText");

    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const saveBtn = document.getElementById("saveBtn");

    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const clearSearchBtn = document.getElementById("clearSearchBtn");
    const searchInfo = document.getElementById("searchInfo");
    const resultsContainer = document.getElementById("resultsContainer");

    const goToInput = document.getElementById("goToInput");
    const goToBtn = document.getElementById("goToBtn");
    const downloadBtn = document.getElementById("downloadBtn");
    const clearDocBtn = document.getElementById("clearDocBtn");

    let currentBookId = null;
    let currentPage = 1;
    let totalPages = 1;
    let pollTimer = null;

    function saveState(extra = {}) {
        const state = {
            bookId: currentBookId,
            currentPage,
            totalPages,
            processing: false,
            ...extra
        };
        localStorage.setItem("ocr_workspace_state", JSON.stringify(state));
    }

    function clearState() {
        localStorage.removeItem("ocr_workspace_state");
    }

    function getSavedState() {
        try {
            const raw = localStorage.getItem("ocr_workspace_state");
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    }

    function setReaderControlsEnabled(enabled) {
        searchInput.disabled = !enabled;
        searchBtn.disabled = !enabled;
        clearSearchBtn.disabled = !enabled;
        goToInput.disabled = !enabled;
        goToBtn.disabled = !enabled;
        saveBtn.disabled = !enabled;
        downloadBtn.disabled = !enabled;

        if (!enabled) {
            prevBtn.disabled = true;
            nextBtn.disabled = true;
        } else {
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
        }
    }

    function clearSearchUI() {
        searchInput.value = "";
        searchInfo.textContent = "";
        resultsContainer.innerHTML = "";
    }

    function resetWorkspace() {
        stopPolling();
        clearState();

        currentBookId = null;
        currentPage = 1;
        totalPages = 1;

        uploadForm.reset();
        pageImage.src = "";
        pageText.value = "";
        pageInfo.textContent = "Страна 1 / 1";

        clearSearchUI();
        viewerSection.style.display = "none";
        setReaderControlsEnabled(false);

        statusMessage.textContent = "Работниот простор е исчистен. Може да прикачиш нов документ.";
    }

    function stopPolling() {
        if (pollTimer) {
            clearTimeout(pollTimer);
            pollTimer = null;
        }
    }

    async function loadPage(pageNumber) {
        if (!currentBookId) return;

        try {
            const response = await fetch(`/book/${currentBookId}/page/${pageNumber}`);
            const data = await response.json();

            if (!data.success) {
                statusMessage.textContent = data.message || "Грешка при вчитување на страна.";
                return;
            }

            currentPage = data.page_number;
            totalPages = data.total_pages;

            pageInfo.textContent = `Страна ${currentPage} / ${totalPages}`;
            pageImage.src = data.image_url;
            pageText.value = data.text;

            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;

            saveState({ processing: false });
        } catch (error) {
            statusMessage.textContent = `Грешка при вчитување на страна: ${error.message}`;
            console.error(error);
        }
    }

    async function pollStatus(bookId) {
        stopPolling();

        try {
            const response = await fetch(`/status/${bookId}`);
            const data = await response.json();

            if (!data.success) {
                statusMessage.textContent = data.message || "Грешка при проверка на статус.";
                return;
            }

            if (data.status === "queued" || data.status === "processing") {
                currentBookId = bookId;
                totalPages = data.total_pages || 1;

                viewerSection.style.display = "none";
                setReaderControlsEnabled(false);

                if (data.total_pages > 0) {
                    statusMessage.textContent = `${data.message} (${data.current_page}/${data.total_pages})`;
                } else {
                    statusMessage.textContent = data.message;
                }

                saveState({
                    processing: true,
                    bookId: bookId,
                    currentPage: 1,
                    totalPages: data.total_pages || 1
                });

                pollTimer = setTimeout(() => pollStatus(bookId), 2000);
                return;
            }

            if (data.status === "completed") {
                currentBookId = bookId;
                currentPage = 1;
                totalPages = data.total_pages || 1;

                statusMessage.textContent = `Книгата е успешно обработена. Вкупно страни: ${totalPages}`;
                viewerSection.style.display = "block";
                clearSearchUI();
                setReaderControlsEnabled(true);

                saveState({ processing: false });
                await loadPage(1);
                return;
            }

            if (data.status === "error") {
                statusMessage.textContent = data.message || "Настана грешка при OCR обработка.";
                clearState();
            }
        } catch (error) {
            statusMessage.textContent = `Грешка при проверка на статус: ${error.message}`;
            console.error(error);
        }
    }

    async function restoreStateIfExists() {
        const saved = getSavedState();
        if (!saved || !saved.bookId) {
            setReaderControlsEnabled(false);
            return;
        }

        currentBookId = saved.bookId;
        currentPage = saved.currentPage || 1;
        totalPages = saved.totalPages || 1;

        if (saved.processing) {
            statusMessage.textContent = "Се обновува статусот на OCR обработката...";
            await pollStatus(saved.bookId);
            return;
        }

        viewerSection.style.display = "block";
        setReaderControlsEnabled(true);
        statusMessage.textContent = "Вчитана е последно обработената книга.";
        await loadPage(currentPage);
    }

    setReaderControlsEnabled(false);

    uploadForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            statusMessage.textContent = "Избери PDF фајл.";
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadBtn.disabled = true;
        fileInput.disabled = true;
        viewerSection.style.display = "none";
        stopPolling();

        statusMessage.textContent =
            "Документот се прикачува и ќе започне OCR обработка. Ова може да потрае неколку минути.";

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                currentBookId = data.book_id;
                currentPage = 1;
                totalPages = 1;

                saveState({
                    processing: true,
                    bookId: currentBookId,
                    currentPage: 1,
                    totalPages: 1
                });

                await pollStatus(currentBookId);
            } else {
                statusMessage.textContent = data.message || "Настана грешка.";
            }
        } catch (error) {
            statusMessage.textContent = `Грешка при прикачување: ${error.message}`;
            console.error(error);
        } finally {
            uploadBtn.disabled = false;
            fileInput.disabled = false;
        }
    });

    prevBtn.addEventListener("click", async function () {
        if (currentPage > 1) {
            await loadPage(currentPage - 1);
        }
    });

    nextBtn.addEventListener("click", async function () {
        if (currentPage < totalPages) {
            await loadPage(currentPage + 1);
        }
    });

    goToBtn.addEventListener("click", async function () {
        const targetPage = parseInt(goToInput.value, 10);

        if (!targetPage || targetPage < 1 || targetPage > totalPages) {
            statusMessage.textContent = `Внеси валиден број од 1 до ${totalPages}.`;
            return;
        }

        statusMessage.textContent = "";
        await loadPage(targetPage);
    });

    goToInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            goToBtn.click();
        }
    });

    searchBtn.addEventListener("click", async function () {
        if (!currentBookId) {
            statusMessage.textContent = "Прво прикачи книга.";
            return;
        }

        const query = searchInput.value.trim();

        if (!query) {
            searchInfo.textContent = "Внеси збор или фраза за пребарување.";
            resultsContainer.innerHTML = "";
            return;
        }

        searchInfo.textContent = "Се пребарува...";
        resultsContainer.innerHTML = "";

        try {
            const response = await fetch(`/search/${currentBookId}?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (!data.success) {
                searchInfo.textContent = data.message || "Грешка при пребарување.";
                return;
            }

            if (data.count === 0) {
                searchInfo.textContent = `Нема резултати за "${data.query}".`;
                return;
            }

            searchInfo.textContent = `Пронајдени ${data.count} резултати за "${data.query}".`;

            data.results.forEach(result => {
                const card = document.createElement("div");
                card.className = "result-card";

                const title = document.createElement("h4");
                title.textContent = `Страна ${result.page_number}`;

                const snippet = document.createElement("p");
                snippet.textContent = result.snippet;

                const openBtn = document.createElement("button");
                openBtn.type = "button";
                openBtn.textContent = "Отвори страна";
                openBtn.addEventListener("click", async function () {
                    await loadPage(result.page_number);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                });

                card.appendChild(title);
                card.appendChild(snippet);
                card.appendChild(openBtn);

                resultsContainer.appendChild(card);
            });
        } catch (error) {
            searchInfo.textContent = `Грешка при пребарување: ${error.message}`;
            console.error(error);
        }
    });

    clearSearchBtn.addEventListener("click", function () {
        clearSearchUI();
    });

    saveBtn.addEventListener("click", async function () {
        if (!currentBookId) return;

        try {
            const response = await fetch("/save-correction", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    book_id: currentBookId,
                    page_number: currentPage,
                    text: pageText.value
                })
            });

            const data = await response.json();

            if (data.success) {
                statusMessage.textContent = "Корекцијата е успешно зачувана.";
                saveState({ processing: false });
            } else {
                statusMessage.textContent = data.message || "Грешка при зачувување.";
            }
        } catch (error) {
            statusMessage.textContent = `Грешка при зачувување: ${error.message}`;
            console.error(error);
        }
    });

    downloadBtn.addEventListener("click", function () {
        if (!currentBookId) {
            statusMessage.textContent = "Прво прикачи книга.";
            return;
        }

        window.location.href = `/download/${currentBookId}`;
    });

    clearDocBtn.addEventListener("click", function () {
        resetWorkspace();
    });

    restoreStateIfExists();
});