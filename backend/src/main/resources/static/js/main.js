/**
 * Wires up event listeners: file selection, drag-and-drop, scan, reset.
 */

(() => {
    let selectedFile = null;

    function handleFileSelected(file) {
        if (!file || !file.type.startsWith("image/")) {
            UI.showError("Please select a valid image file.");
            return;
        }

        selectedFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            UI.setPreviewImage(e.target.result);
        };
        reader.readAsDataURL(file);

        UI.setScanButtonEnabled(true);
        UI.showIdle();
    }

    async function handleScan() {
        if (!selectedFile) return;

        UI.setScanButtonEnabled(false);
        UI.showLoading();

        try {
            const result = await API.identify(selectedFile);
            UI.renderResult(result);
        } catch (err) {
            UI.showError(err.message || "Unexpected error occurred.");
        } finally {
            UI.setScanButtonEnabled(true);
        }
    }

    function handleReset() {
        selectedFile = null;
        UI.reset();
    }

    function init() {
        const { uploadZone, fileInput, btnScan, btnReset } = UI.el;

        uploadZone.addEventListener("click", (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        fileInput.addEventListener("click", (e) => {
            e.stopPropagation();
        });

        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) handleFileSelected(file);
        });

        // Drag and drop
        ["dragenter", "dragover"].forEach((eventName) => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.add("drag-over");
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                uploadZone.classList.remove("drag-over");
            });
        });

        uploadZone.addEventListener("drop", (e) => {
            const file = e.dataTransfer.files[0];
            if (file) handleFileSelected(file);
        });

        btnScan.addEventListener("click", handleScan);
        btnReset.addEventListener("click", handleReset);

        UI.setScanButtonEnabled(false);
    }

    document.addEventListener("DOMContentLoaded", init);
})();