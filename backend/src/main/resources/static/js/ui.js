/**
 * Handles all DOM manipulation and screen-state transitions.
 * No fetch/business logic lives here — that's main.js's job.
 */

const UI = (() => {
    const states = {
        idle: document.getElementById("state-idle"),
        loading: document.getElementById("state-loading"),
        error: document.getElementById("state-error"),
        result: document.getElementById("state-result"),
    };

    const el = {
        loadingText: document.getElementById("loading-text"),
        errorText: document.getElementById("error-text"),

        resultId: document.getElementById("result-id"),
        resultName: document.getElementById("result-name"),
        resultSprite: document.getElementById("result-sprite"),
        resultTypes: document.getElementById("result-types"),
        confidenceValue: document.getElementById("confidence-value"),
        confidenceBar: document.getElementById("confidence-bar"),

        uploadZone: document.getElementById("upload-zone"),
        uploadZoneInner: document.getElementById("upload-zone-inner"),
        previewImage: document.getElementById("preview-image"),
        fileInput: document.getElementById("file-input"),

        detailsEmpty: document.getElementById("details-empty"),
        detailsContent: document.getElementById("details-content"),
        detailsName: document.getElementById("details-name"),
        detailsFlavor: document.getElementById("details-flavor"),
        detailHeight: document.getElementById("detail-height"),
        detailWeight: document.getElementById("detail-weight"),
        detailAbilities: document.getElementById("detail-abilities"),
        statsList: document.getElementById("stats-list"),
        altMatches: document.getElementById("alt-matches"),
        altMatchesList: document.getElementById("alt-matches-list"),

        btnScan: document.getElementById("btn-scan"),
        btnReset: document.getElementById("btn-reset"),
    };

    const loadingMessages = ["SCANNING...", "ANALYZING...", "IDENTIFYING...", "PROCESSING..."];
    let loadingInterval = null;

    function showScreenState(name) {
        Object.entries(states).forEach(([key, node]) => {
            node.classList.toggle("hidden", key !== name);
        });
    }

    function showLoading() {
        showScreenState("loading");
        let i = 0;
        clearInterval(loadingInterval);
        loadingInterval = setInterval(() => {
            i = (i + 1) % loadingMessages.length;
            el.loadingText.textContent = loadingMessages[i];
        }, 700);
    }

    function stopLoadingAnimation() {
        clearInterval(loadingInterval);
    }

    function showError(message) {
        stopLoadingAnimation();
        el.errorText.textContent = message;
        showScreenState("error");
        el.detailsEmpty.classList.remove("hidden");
        el.detailsContent.classList.add("hidden");
    }

    function showIdle() {
        stopLoadingAnimation();
        showScreenState("idle");
    }

    function setPreviewImage(dataUrl) {
        el.previewImage.src = dataUrl;
        el.previewImage.classList.remove("hidden");
        el.uploadZoneInner.classList.add("hidden");
    }

    function clearPreviewImage() {
        el.previewImage.src = "";
        el.previewImage.classList.add("hidden");
        el.uploadZoneInner.classList.remove("hidden");
        el.fileInput.value = "";
    }

    function setScanButtonEnabled(enabled) {
        el.btnScan.disabled = !enabled;
    }

    const TYPE_COLOR_VAR = {
        normal: "--type-normal", fire: "--type-fire", water: "--type-water",
        grass: "--type-grass", electric: "--type-electric", ice: "--type-ice",
        fighting: "--type-fighting", poison: "--type-poison", ground: "--type-ground",
        flying: "--type-flying", psychic: "--type-psychic", bug: "--type-bug",
        rock: "--type-rock", ghost: "--type-ghost", dragon: "--type-dragon",
        dark: "--type-dark", steel: "--type-steel", fairy: "--type-fairy",
    };

    function renderResult(data) {
        stopLoadingAnimation();

        // --- Screen (left panel) ---
        el.resultId.textContent = `#${String(data.id).padStart(3, "0")}`;
        el.resultName.textContent = data.name;
        el.resultSprite.src = data.spriteUrl || "";

        el.resultTypes.innerHTML = "";
        data.types.forEach((type) => {
            const badge = document.createElement("span");
            badge.className = "type-badge";
            badge.textContent = type;
            const colorVar = TYPE_COLOR_VAR[type] || "--type-normal";
            badge.style.background = `var(${colorVar})`;
            el.resultTypes.appendChild(badge);
        });

        const confidencePct = Math.round(data.confidence * 100);
        el.confidenceValue.textContent = `${confidencePct}%`;
        el.confidenceBar.style.width = "0%";
        requestAnimationFrame(() => {
            el.confidenceBar.style.width = `${confidencePct}%`;
        });

        showScreenState("result");

        // --- Details panel (right side) ---
        el.detailsEmpty.classList.add("hidden");
        el.detailsContent.classList.remove("hidden");

        el.detailsName.textContent = `${data.name} #${String(data.id).padStart(3, "0")}`;
        el.detailsFlavor.textContent = data.flavorText;
        el.detailHeight.textContent = `${data.heightMeters} m`;
        el.detailWeight.textContent = `${data.weightKg} kg`;
        el.detailAbilities.textContent = data.abilities.join(", ");

        renderStats(data.stats);
        renderAlternatives(data.alternativeMatches);
    }

    function renderStats(stats) {
        const statEntries = [
            ["HP", stats.hp],
            ["Attack", stats.attack],
            ["Defense", stats.defense],
            ["Sp. Atk", stats.specialAttack],
            ["Sp. Def", stats.specialDefense],
            ["Speed", stats.speed],
        ];

        el.statsList.innerHTML = "";
        statEntries.forEach(([label, value]) => {
            const row = document.createElement("div");
            row.className = "stat-row";

            const pct = Math.min(100, (value / 180) * 100); // 180 ~ typical max base stat

            row.innerHTML = `
                <span class="stat-name">${label}</span>
                <div class="stat-track"><div class="stat-fill" style="width:0%"></div></div>
                <span class="stat-value">${value}</span>
            `;
            el.statsList.appendChild(row);

            requestAnimationFrame(() => {
                row.querySelector(".stat-fill").style.width = `${pct}%`;
            });
        });
    }

    function renderAlternatives(alternatives) {
        if (!alternatives || alternatives.length <= 1) {
            el.altMatches.classList.add("hidden");
            return;
        }
        el.altMatches.classList.remove("hidden");
        el.altMatchesList.innerHTML = "";

        // Skip the first one (that's the main match already shown above)
        alternatives.slice(1).forEach((alt) => {
            const item = document.createElement("div");
            item.className = "alt-match-item";
            item.innerHTML = `
                <span>${alt.className}</span>
                <span>${Math.round(alt.probability * 100)}%</span>
            `;
            el.altMatchesList.appendChild(item);
        });
    }

    function reset() {
        clearPreviewImage();
        showIdle();
        setScanButtonEnabled(false);
        el.detailsEmpty.classList.remove("hidden");
        el.detailsContent.classList.add("hidden");
    }

    return {
        el,
        showLoading,
        showError,
        showIdle,
        setPreviewImage,
        clearPreviewImage,
        setScanButtonEnabled,
        renderResult,
        reset,
    };
})();