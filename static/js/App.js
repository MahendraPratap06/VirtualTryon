// ── State ──────────────────────────────────────────────────────────────────────
const state = {
    "person-1": null,
    "person-2": null,
    "person-3": null,
    shirt:      null,
    pants:      null,
    dress:      null,
};

let visiblePersonSlots = 1;  // tracks how many person slots are shown

const STAGES = [
    { pct: 10, stage: "Validating your images...",        lstep: 1 },
    { pct: 30, stage: "Preparing images for AI...",       lstep: 2 },
    { pct: 80, stage: "AI is styling your outfit...",     lstep: 3 },
    { pct: 95, stage: "Putting the finishing touches...", lstep: 4 },
];


// ── Add Pose (dynamic) ─────────────────────────────────────────────────────────
function addPose() {
    if (visiblePersonSlots >= 3) return;

    visiblePersonSlots++;
    const card = document.getElementById(`card-person-${visiblePersonSlots}`);
    card.style.display  = "flex";
    card.style.opacity  = "0";
    card.style.transform = "translateY(12px)";
    requestAnimationFrame(() => {
        card.style.transition = "opacity 0.35s ease, transform 0.35s ease";
        card.style.opacity    = "1";
        card.style.transform  = "translateY(0)";
    });

    // Hide add button if at max
    if (visiblePersonSlots >= 3) {
        document.getElementById("add-pose-btn").style.display = "none";
    }

    updateUI();
}


// ── Upload trigger ─────────────────────────────────────────────────────────────
function triggerUpload(slot) {
    document.getElementById(`input-${slot}`).click();
}


// ── Handle file ────────────────────────────────────────────────────────────────
function handleFile(slot, input) {
    const file = input.files[0];
    if (!file) return;
    state[slot] = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById(`preview-${slot}`).src = e.target.result;
    };
    reader.readAsDataURL(file);

    document.getElementById(`zone-${slot}`).classList.add("has-file");
    document.getElementById(`name-${slot}`).textContent = truncate(file.name, 24);
    updateUI();
}


// ── Remove file ────────────────────────────────────────────────────────────────
function removeFile(e, slot) {
    e.stopPropagation();
    state[slot] = null;
    document.getElementById(`input-${slot}`).value = "";
    document.getElementById(`preview-${slot}`).src = "";
    document.getElementById(`zone-${slot}`).classList.remove("has-file");
    document.getElementById(`name-${slot}`).textContent = "No file selected";
    updateUI();
}


// ── Update UI state ────────────────────────────────────────────────────────────
function updateUI() {
    const btn  = document.getElementById("tryon-btn");
    const bar  = document.getElementById("status-bar");
    const icon = document.getElementById("status-icon");
    const txt  = document.getElementById("status-text");
    const note = document.getElementById("cta-note");

    const hasPerson   = state["person-1"];
    const hasGarment  = state.shirt || state.pants || state.dress;
    const poseCount   = [state["person-1"], state["person-2"], state["person-3"]].filter(Boolean).length;

    if (!hasPerson && !hasGarment) {
        btn.disabled = true; bar.className = "status-bar";
        icon.textContent = "○";
        txt.textContent  = "Upload your photo and at least one garment to get started";
    } else if (!hasPerson) {
        btn.disabled = true; bar.className = "status-bar";
        icon.textContent = "○";
        txt.textContent  = "Garment added — now upload your photo";
    } else if (!hasGarment) {
        btn.disabled = true; bar.className = "status-bar";
        icon.textContent = "○";
        txt.textContent  = "Photo added — now upload a garment";
    } else {
        btn.disabled = false; bar.className = "status-bar ready";
        icon.textContent = "✓";
        if (poseCount > 1) {
            txt.textContent = `✓ ${poseCount} poses selected — AI will generate ${poseCount} results`;
        } else {
            txt.textContent = "✓ Ready — click Generate Outfit";
        }
    }

    // Update note text
    const poseCount2 = [state["person-1"], state["person-2"], state["person-3"]].filter(Boolean).length;
    note.textContent = poseCount2 > 1
        ? `Powered by FASHN VTON v1.5 · ${poseCount2} poses · ~${poseCount2 * 60}s total`
        : "Powered by FASHN VTON v1.5 · ~30–90s per pose";
}


// ── Progress ring ──────────────────────────────────────────────────────────────
let progressTimer = null;
let slowMsgTimer  = null;
let currentProgress = 0;

function startProgress(poseCount) {
    currentProgress = 0;
    let stageIdx = 0;

    progressTimer = setInterval(() => {
        const target = stageIdx < STAGES.length ? STAGES[stageIdx].pct : 95;
        if (currentProgress < target) {
            currentProgress += 0.3;
            setProgress(currentProgress);
        }
        if (stageIdx < STAGES.length && currentProgress >= STAGES[stageIdx].pct) {
            const s = STAGES[stageIdx];
            document.getElementById("loading-stage").textContent = s.stage;
            for (let i = 1; i < s.lstep; i++) {
                const el = document.getElementById(`lstep-${i}`);
                el.className = "lstep done";
                el.textContent = "✓ " + el.textContent.replace(/^[○→✓] /, "");
            }
            const cur = document.getElementById(`lstep-${s.lstep}`);
            cur.className = "lstep active";
            cur.textContent = "→ " + cur.textContent.replace(/^[○→✓] /, "");
            stageIdx++;
        }
    }, 200);

    // 45s patience message
    slowMsgTimer = setTimeout(() => {
        const stage = document.getElementById("loading-stage");
        stage.textContent = poseCount > 1
            ? `Processing ${poseCount} poses — thank you for your patience! ☕`
            : "Our model is working hard — thank you for your patience! ☕";
        stage.style.color = "var(--gold)";
    }, 45000);
}

function stopProgress(success) {
    clearInterval(progressTimer);
    clearTimeout(slowMsgTimer);
    document.getElementById("loading-stage").style.color = "";
    if (success) {
        setProgress(100);
        setStep("step-3");
        for (let i = 1; i <= 4; i++) {
            const el = document.getElementById(`lstep-${i}`);
            el.className = "lstep done";
            el.textContent = "✓ " + el.textContent.replace(/^[○→✓] /, "");
        }
    }
}

function setProgress(pct) {
    const offset = 276.46 - (pct / 100) * 276.46;
    document.querySelector(".ring-fill").style.strokeDashoffset = offset;
    document.getElementById("ring-pct").textContent = Math.round(pct) + "%";
}

function setStep(activeId) {
    ["step-1","step-2","step-3"].forEach(id => document.getElementById(id).className = "step");
    document.getElementById(activeId).className = "step active";
}


// ── Submit ─────────────────────────────────────────────────────────────────────
async function submitTryOn() {
    hide("result-panel"); hide("error-panel");
    hide("upload-panel"); show("loading-panel");
    setStep("step-2");

    const poseCount = [state["person-1"], state["person-2"], state["person-3"]].filter(Boolean).length;
    startProgress(poseCount);

    const formData = new FormData();
    formData.append("person_image_1", state["person-1"]);
    if (state["person-2"]) formData.append("person_image_2", state["person-2"]);
    if (state["person-3"]) formData.append("person_image_3", state["person-3"]);
    if (state.shirt)  formData.append("shirt_image", state.shirt);
    if (state.pants)  formData.append("pants_image", state.pants);
    if (state.dress)  formData.append("dress_image", state.dress);

    try {
        const response = await fetch("/tryon", { method: "POST", body: formData });
        const data     = await response.json();

        stopProgress(response.ok);
        await sleep(600);
        hide("loading-panel");

        if (!response.ok) {
            showError(data.detail || "Something went wrong. Please try again.");
            show("upload-panel"); setStep("step-1"); return;
        }

        buildResultGallery(data.result_image_urls, data.pose_count);
        show("result-panel");
        document.getElementById("result-panel").scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        stopProgress(false); hide("loading-panel");
        show("upload-panel"); setStep("step-1");
        showError("Unable to reach the server. Please check your connection and try again.");
    }
}


// ── Build result gallery ───────────────────────────────────────────────────────
function buildResultGallery(urls, count) {
    const gallery  = document.getElementById("result-gallery");
    const subtitle = document.getElementById("result-subtitle");

    subtitle.textContent = count > 1
        ? `${count} outfit variations — pick your favourite`
        : "Your outfit is ready to download";

    gallery.innerHTML = "";

    urls.forEach((url, i) => {
        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <div class="result-img-wrap">
                <img class="result-img" src="${url}" alt="Outfit ${i+1}"/>
                <div class="result-img-glow"></div>
            </div>
            <div class="result-card-footer">
                <span class="result-pose-label">Pose ${i + 1}</span>
                <a class="btn-download" href="${url}" download="outfit_pose_${i+1}.png">
                    &#8595; Download
                </a>
            </div>
        `;
        gallery.appendChild(card);
    });
}


// ── Reset ──────────────────────────────────────────────────────────────────────
function resetAll() {
    // Reset all file states
    ["person-1","person-2","person-3","shirt","pants","dress"].forEach(slot => {
        state[slot] = null;
        const input = document.getElementById(`input-${slot}`);
        if (input) input.value = "";
        const preview = document.getElementById(`preview-${slot}`);
        if (preview) preview.src = "";
        const zone = document.getElementById(`zone-${slot}`);
        if (zone) zone.classList.remove("has-file");
        const name = document.getElementById(`name-${slot}`);
        if (name) name.textContent = "No file selected";
    });

    // Hide extra person slots
    document.getElementById("card-person-2").style.display = "none";
    document.getElementById("card-person-3").style.display = "none";
    document.getElementById("add-pose-btn").style.display  = "flex";
    visiblePersonSlots = 1;

    // Reset loading steps
    const labels = ["Validating your images","Preparing images for AI","AI is styling your outfit","Putting the finishing touches"];
    for (let i = 1; i <= 4; i++) {
        const el = document.getElementById(`lstep-${i}`);
        el.className = "lstep";
        el.textContent = "○ " + labels[i-1];
    }

    hide("result-panel"); hide("error-panel");
    show("upload-panel"); setStep("step-1");
    setProgress(0);
    document.getElementById("loading-stage").textContent = "Initialising pipeline...";
    document.getElementById("loading-stage").style.color = "";
    document.getElementById("result-gallery").innerHTML = "";
    updateUI();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetError() {
    hide("error-panel"); show("upload-panel"); setStep("step-1");
}


// ── Drag & drop ────────────────────────────────────────────────────────────────
["person-1","person-2","person-3","shirt","pants","dress"].forEach(slot => {
    const zone = document.getElementById(`zone-${slot}`);
    if (!zone) return;
    zone.addEventListener("dragover",  (e) => { e.preventDefault(); zone.classList.add("drag-over"); });
    zone.addEventListener("dragleave", ()  => zone.classList.remove("drag-over"));
    zone.addEventListener("drop", (e) => {
        e.preventDefault(); zone.classList.remove("drag-over");
        const file = e.dataTransfer.files[0]; if (!file) return;
        const dt = new DataTransfer(); dt.items.add(file);
        const input = document.getElementById(`input-${slot}`);
        input.files = dt.files; handleFile(slot, input);
    });
});


// ── Helpers ────────────────────────────────────────────────────────────────────
function show(id) { document.getElementById(id).hidden = false; }
function hide(id) { document.getElementById(id).hidden = true; }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function truncate(s, max) { return s.length > max ? s.slice(0, max-3) + "..." : s; }
function showError(msg) {
    document.getElementById("error-msg").textContent = msg;
    show("error-panel");
}