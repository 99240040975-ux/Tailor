/* =========================================================
   TailorConnect - Location Cascade
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initLocationCascade();
});


function initLocationCascade() {
    const stateSelect = document.querySelector(
        "#state, #state_id, [data-location-state]"
    );

    const districtSelect = document.querySelector(
        "#district, #district_id, [data-location-district]"
    );

    const talukSelect = document.querySelector(
        "#taluk, #taluk_id, [data-location-taluk]"
    );

    const citySelect = document.querySelector(
        "#city, #city_id, [data-location-city]"
    );

    if (!stateSelect && !districtSelect) return;

    if (stateSelect) {
        stateSelect.addEventListener("change", () => {
            resetSelect(districtSelect);
            resetSelect(talukSelect);
            resetSelect(citySelect);

            const stateId = stateSelect.value;

            if (!stateId) return;

            loadLocations(
                "districts",
                stateId,
                districtSelect
            );
        });
    }

    if (districtSelect) {
        districtSelect.addEventListener("change", () => {
            resetSelect(talukSelect);
            resetSelect(citySelect);

            const districtId = districtSelect.value;

            if (!districtId) return;

            loadLocations(
                "taluks",
                districtId,
                talukSelect
            );
        });
    }

    if (talukSelect) {
        talukSelect.addEventListener("change", () => {
            resetSelect(citySelect);

            const talukId = talukSelect.value;

            if (!talukId) return;

            loadLocations(
                "cities",
                talukId,
                citySelect
            );
        });
    }
}


/* =========================================================
   LOAD LOCATIONS
   ========================================================= */

async function loadLocations(type, parentId, select) {
    if (!select) return;

    setSelectLoading(select);

    try {
        const response = await fetch(
            `/locations/${type}?parent_id=${encodeURIComponent(parentId)}`,
            {
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                `Location request failed: ${response.status}`
            );
        }

        const data = await response.json();

        populateSelect(select, normalizeLocations(data));

    } catch (error) {
        console.error("Location loading error:", error);

        resetSelect(select);

        TailorConnect.showToast(
            "Unable to load locations. Please try again.",
            "error"
        );
    } finally {
        select.disabled = false;
    }
}


/* =========================================================
   NORMALIZE API RESPONSE
   ========================================================= */

function normalizeLocations(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.locations)) {
        return data.locations;
    }

    if (Array.isArray(data.results)) {
        return data.results;
    }

    if (Array.isArray(data.data)) {
        return data.data;
    }

    return [];
}


/* =========================================================
   POPULATE SELECT
   ========================================================= */

function populateSelect(select, locations) {
    select.innerHTML = "";

    const placeholder = document.createElement("option");

    placeholder.value = "";
    placeholder.textContent = "Select an option";

    select.appendChild(placeholder);

    locations.forEach((location) => {
        const option = document.createElement("option");

        const id =
            location.id ??
            location.value ??
            location.code;

        const name =
            location.name ??
            location.label ??
            location.title;

        option.value = id ?? "";
        option.textContent = name ?? "Unknown";

        select.appendChild(option);
    });

    select.disabled = locations.length === 0;
}


/* =========================================================
   SELECT HELPERS
   ========================================================= */

function resetSelect(select) {
    if (!select) return;

    select.innerHTML = "";

    const option = document.createElement("option");

    option.value = "";
    option.textContent = "Select an option";

    select.appendChild(option);

    select.disabled = true;
}


function setSelectLoading(select) {
    if (!select) return;

    select.innerHTML = "";

    const option = document.createElement("option");

    option.value = "";
    option.textContent = "Loading...";

    select.appendChild(option);

    select.disabled = true;
}


/* =========================================================
   BROWSER GEOLOCATION
   ========================================================= */

window.TailorConnectLocation = {

    detect() {
        if (!navigator.geolocation) {
            TailorConnect.showToast(
                "Location detection is not supported by this browser.",
                "error"
            );

            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const latitude =
                    position.coords.latitude;

                const longitude =
                    position.coords.longitude;

                await resolveCoordinates(
                    latitude,
                    longitude
                );
            },
            () => {
                TailorConnect.showToast(
                    "Location access was not available. Please select your location manually.",
                    "info"
                );
            },
            {
                enableHighAccuracy: false,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    }
};


/* =========================================================
   COORDINATE RESOLUTION
   ========================================================= */

async function resolveCoordinates(
    latitude,
    longitude
) {
    try {
        const response = await fetch(
            `/locations/reverse-geocode?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`,
            {
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error("Reverse geocoding failed");
        }

        const data = await response.json();

        applyDetectedLocation(data);

    } catch (error) {
        console.error(
            "Reverse location error:",
            error
        );

        TailorConnect.showToast(
            "We couldn't determine your location. Please choose it manually.",
            "info"
        );
    }
}


/* =========================================================
   APPLY DETECTED LOCATION
   ========================================================= */

function applyDetectedLocation(data) {
    if (!data) return;

    const mappings = {
        state: data.state_id ?? data.state,
        district: data.district_id ?? data.district,
        taluk: data.taluk_id ?? data.taluk,
        city: data.city_id ?? data.city
    };

    Object.entries(mappings).forEach(
        ([field, value]) => {
            if (!value) return;

            const element = document.querySelector(
                `#${field}, #${field}_id, [data-location-${field}]`
            );

            if (!element) return;

            const matchingOption =
                Array.from(element.options).find(
                    (option) =>
                        option.value == value ||
                        option.textContent
                            .trim()
                            .toLowerCase() ===
                            String(value)
                                .trim()
                                .toLowerCase()
                );

            if (matchingOption) {
                element.value =
                    matchingOption.value;

                element.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );
            }
        }
    );
}