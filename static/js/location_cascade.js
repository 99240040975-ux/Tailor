/**
 * Location Cascade Helper for Local Tailor Connect
 * Handles dynamic cascading dropdowns:
 * State -> District -> Taluk -> City / Town -> Village / Area
 * Also provides HTML5 GPS location auto-detection.
 */

class LocationCascade {
    constructor(options = {}) {
        this.apiBase = options.apiBase || '/api/locations';
        this.stateSelect = document.getElementById(options.stateSelectId || 'state_id');
        this.districtSelect = document.getElementById(options.districtSelectId || 'district_id');
        this.talukSelect = document.getElementById(options.talukSelectId || 'taluk_id');
        this.cityTownSelect = document.getElementById(options.cityTownSelectId || 'city_town_id');
        this.villageSelect = document.getElementById(options.villageSelectId || 'village_id');
        
        // Hidden input helpers if city and town share a composite dropdown
        this.cityInput = document.getElementById(options.cityInputId || 'city_id');
        this.townInput = document.getElementById(options.townInputId || 'town_id');
        
        // Lat / Long elements
        this.latInput = document.getElementById(options.latInputId || 'latitude');
        this.lngInput = document.getElementById(options.lngInputId || 'longitude');
        this.geoBtn = document.getElementById(options.geoBtnId || 'detectLocationBtn');
        this.geoStatus = document.getElementById(options.geoStatusId || 'geoStatus');

        this.init();
    }

    async init() {
        if (this.stateSelect) {
            await this.loadStates();
            this.stateSelect.addEventListener('change', () => this.onStateChange());
        }
        if (this.districtSelect) {
            this.districtSelect.addEventListener('change', () => this.onDistrictChange());
        }
        if (this.talukSelect) {
            this.talukSelect.addEventListener('change', () => this.onTalukChange());
        }
        if (this.cityTownSelect) {
            this.cityTownSelect.addEventListener('change', () => this.onCityTownChange());
        }
        if (this.geoBtn) {
            this.geoBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.detectCurrentLocation();
            });
        }
    }

    resetSelect(selectElement, defaultText) {
        if (!selectElement) return;
        selectElement.innerHTML = `<option value="">${defaultText}</option>`;
        selectElement.disabled = true;
    }

    setSelectLoading(selectElement, loadingText = 'Loading...') {
        if (!selectElement) return;
        selectElement.innerHTML = `<option value="">⏳ ${loadingText}</option>`;
        selectElement.disabled = true;
    }

    async fetchJson(url) {
        try {
            const resp = await fetch(url);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            return await resp.json();
        } catch (err) {
            console.error('Error fetching location data from', url, err);
            return [];
        }
    }

    async loadStates() {
        this.setSelectLoading(this.stateSelect, 'Loading States...');
        const states = await this.fetchJson(`${this.apiBase}/states`);
        this.resetSelect(this.stateSelect, '-- Select State --');
        this.stateSelect.disabled = false;

        let tnId = null;
        states.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name;
            if (s.name.toUpperCase().includes('TAMIL NADU') || s.code === '33') {
                tnId = s.id;
            }
            this.stateSelect.appendChild(opt);
        });

        // Pre-select Tamil Nadu by default
        if (tnId) {
            this.stateSelect.value = tnId;
            await this.onStateChange(tnId);
        }
    }

    async onStateChange(forceStateId = null) {
        const stateId = forceStateId || (this.stateSelect ? this.stateSelect.value : null);
        this.resetSelect(this.districtSelect, '-- Select District --');
        this.resetSelect(this.talukSelect, '-- Select Taluk / Sub-district --');
        this.resetSelect(this.cityTownSelect, '-- Select City / Town --');
        this.resetSelect(this.villageSelect, '-- Select Village / Area --');

        if (!stateId) return;

        this.setSelectLoading(this.districtSelect, 'Loading Districts...');
        const districts = await this.fetchJson(`${this.apiBase}/districts/${stateId}`);
        this.resetSelect(this.districtSelect, '-- Select District (All 38 available) --');
        this.districtSelect.disabled = false;

        districts.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.textContent = d.name;
            this.districtSelect.appendChild(opt);
        });
    }

    async onDistrictChange() {
        const districtId = this.districtSelect ? this.districtSelect.value : null;
        this.resetSelect(this.talukSelect, '-- Select Taluk / Sub-district --');
        this.resetSelect(this.cityTownSelect, '-- Select City / Town --');
        this.resetSelect(this.villageSelect, '-- Select Village / Area --');

        if (!districtId) return;

        this.setSelectLoading(this.talukSelect, 'Loading Taluks...');
        const taluks = await this.fetchJson(`${this.apiBase}/taluks/${districtId}`);
        this.resetSelect(this.talukSelect, '-- Select Taluk / Sub-district --');
        this.talukSelect.disabled = false;

        taluks.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.name;
            this.talukSelect.appendChild(opt);
        });

        // Also load district-level cities in cityTownSelect if present
        if (this.cityTownSelect) {
            const cities = await this.fetchJson(`${this.apiBase}/cities/0?district_id=${districtId}`);
            if (cities.length > 0) {
                this.cityTownSelect.disabled = false;
                this.resetSelect(this.cityTownSelect, '-- Select City / Town (Optional) --');
                const group = document.createElement('optgroup');
                group.label = "Municipal Corporations / Cities";
                cities.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = `city:${c.id}`;
                    opt.textContent = c.name;
                    group.appendChild(opt);
                });
                this.cityTownSelect.appendChild(group);
            }
        }
    }

    async onTalukChange() {
        const talukId = this.talukSelect ? this.talukSelect.value : null;
        const districtId = this.districtSelect ? this.districtSelect.value : null;

        this.resetSelect(this.villageSelect, '-- Select Village / Area --');

        if (!talukId) return;

        // Fetch towns & cities for this taluk
        if (this.cityTownSelect) {
            this.setSelectLoading(this.cityTownSelect, 'Loading Urban Bodies...');
            const [cities, towns] = await Promise.all([
                this.fetchJson(`${this.apiBase}/cities/${talukId}?district_id=${districtId || ''}`),
                this.fetchJson(`${this.apiBase}/towns-by-taluk/${talukId}`)
            ]);

            this.resetSelect(this.cityTownSelect, '-- Select City / Town --');
            this.cityTownSelect.disabled = false;

            if (cities.length > 0) {
                const grpCities = document.createElement('optgroup');
                grpCities.label = "City Corporations";
                cities.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = `city:${c.id}`;
                    opt.textContent = c.name;
                    grpCities.appendChild(opt);
                });
                this.cityTownSelect.appendChild(grpCities);
            }

            if (towns.length > 0) {
                const grpTowns = document.createElement('optgroup');
                grpTowns.label = "Municipalities & Town Panchayats";
                towns.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = `town:${t.id}`;
                    opt.textContent = t.name;
                    grpTowns.appendChild(opt);
                });
                this.cityTownSelect.appendChild(grpTowns);
            }
        }

        // Fetch villages under this taluk
        if (this.villageSelect) {
            this.setSelectLoading(this.villageSelect, 'Loading Revenue Villages...');
            const villages = await this.fetchJson(`${this.apiBase}/villages-by-taluk/${talukId}`);
            this.resetSelect(this.villageSelect, `-- Select Village (${villages.length} available) --`);
            this.villageSelect.disabled = false;

            villages.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.id;
                opt.textContent = v.name;
                this.villageSelect.appendChild(opt);
            });
        }
    }

    onCityTownChange() {
        if (!this.cityTownSelect) return;
        const val = this.cityTownSelect.value;
        if (this.cityInput) this.cityInput.value = '';
        if (this.townInput) this.townInput.value = '';

        if (val.startsWith('city:')) {
            if (this.cityInput) this.cityInput.value = val.replace('city:', '');
        } else if (val.startsWith('town:')) {
            if (this.townInput) this.townInput.value = val.replace('town:', '');
        }
    }

    detectCurrentLocation() {
        if (!navigator.geolocation) {
            if (this.geoStatus) this.geoStatus.textContent = "Geolocation is not supported by your browser.";
            return;
        }

        if (this.geoStatus) this.geoStatus.textContent = "📍 Detecting current GPS coordinates...";

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude.toFixed(6);
                const lng = pos.coords.longitude.toFixed(6);
                if (this.latInput) this.latInput.value = lat;
                if (this.lngInput) this.lngInput.value = lng;
                if (this.geoStatus) {
                    this.geoStatus.innerHTML = `✓ Coordinates locked: <strong style="color: var(--primary);">${lat}, ${lng}</strong>`;
                }
            },
            (err) => {
                console.warn('Geolocation error:', err);
                if (this.geoStatus) {
                    this.geoStatus.textContent = "Unable to automatically detect location. You can enter address manually.";
                }
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
    }
}

// Auto-initialize if standard elements exist on page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('state_id') && document.getElementById('district_id')) {
        window.locationCascade = new LocationCascade();
    }
});
