/* =========================================================
   TailorConnect - Measurements
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initMeasurementForm();
    initMeasurementUnit();
    initMeasurementValidation();
    initMeasurementDelete();
});


/* =========================================================
   MEASUREMENT FORM
   ========================================================= */

function initMeasurementForm() {
    const form = document.querySelector(
        "#measurementForm, [data-measurement-form]"
    );

    if (!form) return;

    form.addEventListener("submit", (event) => {
        const requiredFields = form.querySelectorAll(
            "[required]"
        );

        let valid = true;

        requiredFields.forEach((field) => {
            if (!field.value.trim()) {
                field.classList.add("input-error");
                valid = false;
            } else {
                field.classList.remove("input-error");
            }
        });

        if (!valid) {
            event.preventDefault();

            TailorConnect.showToast(
                "Please complete the required measurement fields.",
                "error"
            );
        }
    });
}


/* =========================================================
   UNIT SELECTION
   ========================================================= */

function initMeasurementUnit() {
    const unitSelectors = document.querySelectorAll(
        "#measurementUnit, [data-measurement-unit]"
    );

    unitSelectors.forEach((selector) => {
        selector.addEventListener("change", () => {
            const unit = selector.value;

            document.querySelectorAll(
                "[data-unit-label]"
            ).forEach((label) => {
                label.textContent = unit;
            });
        });
    });
}


/* =========================================================
   VALIDATION
   ========================================================= */

function initMeasurementValidation() {
    const numberInputs = document.querySelectorAll(
        '.measurement-input, input[data-measurement], input[name="chest"], input[name="waist"], input[name="hip"], input[name="shoulder"], input[name="sleeve"], input[name="neck"], input[name="inseam"], input[name="height"]'
    );

    numberInputs.forEach((input) => {
        input.addEventListener("input", () => {
            const value = Number(input.value);

            if (
                input.value &&
                (Number.isNaN(value) || value <= 0)
            ) {
                input.classList.add("input-error");
            } else {
                input.classList.remove("input-error");
            }
        });
    });
}


/* =========================================================
   DELETE CONFIRMATION
   ========================================================= */

function initMeasurementDelete() {
    const deleteButtons = document.querySelectorAll(
        "[data-delete-measurement]"
    );

    deleteButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const confirmed = window.confirm(
                "Delete this measurement profile?"
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}


/* =========================================================
   GLOBAL MEASUREMENT HELPERS
   ========================================================= */

window.TailorConnectMeasurements = {

    collect(form) {
        if (!form) return {};

        const fields = [
            "profile_name",
            "chest",
            "waist",
            "hip",
            "shoulder",
            "sleeve",
            "neck",
            "inseam",
            "height",
            "unit",
            "notes"
        ];

        const data = {};

        fields.forEach((name) => {
            const field = form.elements[name];

            if (field) {
                data[name] = field.value;
            }
        });

        return data;
    },

    validate(form) {
        if (!form) return false;

        let valid = true;

        form.querySelectorAll(
            "input, select, textarea"
        ).forEach((field) => {
            if (
                field.required &&
                !field.value.trim()
            ) {
                field.classList.add("input-error");
                valid = false;
            }
        });

        return valid;
    }
};


/* =========================================================
   MEASUREMENT STYLES
   ========================================================= */

(function addMeasurementStyles() {
    if (
        document.getElementById(
            "tailorconnect-measurement-styles"
        )
    ) {
        return;
    }

    const style = document.createElement("style");

    style.id =
        "tailorconnect-measurement-styles";

    style.textContent = `
        .input-error {
            border-color: #ef4444 !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, .10) !important;
        }

        .input-error:focus {
            border-color: #ef4444 !important;
        }
    `;

    document.head.appendChild(style);
})();