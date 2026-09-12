// Measurements Dynamic Profile Preview & Helpers
document.addEventListener('DOMContentLoaded', function() {
    const measurementSelect = document.getElementById('measurement_select');
    const previewContainer = document.getElementById('measurement_preview');

    if (measurementSelect && previewContainer) {
        measurementSelect.addEventListener('change', function() {
            const measId = this.value;
            if (!measId) {
                previewContainer.innerHTML = '<p class="text-muted" style="color: var(--text-muted);">No measurement profile selected. Select one above to preview dimensions.</p>';
                return;
            }

            previewContainer.innerHTML = '<p style="color: var(--text-secondary);">Loading measurement profile...</p>';

            fetch(`/measurements/${measId}/json`)
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        previewContainer.innerHTML = `<p style="color: var(--danger);">${data.error}</p>`;
                        return;
                    }

                    const u = data.unit || 'in';
                    previewContainer.innerHTML = `
                        <div class="glass-card" style="padding: 16px; margin-top: 12px; background: rgba(255,255,255,0.02);">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                                <strong style="color: var(--accent-primary);">${data.profile_name}</strong>
                                <span class="badge" style="color: var(--text-secondary);">${data.unit}</span>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; font-size: 0.85rem;">
                                <div><span style="color: var(--text-muted);">Chest:</span> <strong>${data.chest || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Waist:</span> <strong>${data.waist || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Hip:</span> <strong>${data.hip || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Shoulder:</span> <strong>${data.shoulder || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Sleeve:</span> <strong>${data.sleeve || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Neck:</span> <strong>${data.neck || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Inseam:</span> <strong>${data.inseam || '-'} ${u}</strong></div>
                                <div><span style="color: var(--text-muted);">Height:</span> <strong>${data.height || '-'} ${u}</strong></div>
                            </div>
                            ${data.notes ? `<p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px;"><em>Notes:</em> ${data.notes}</p>` : ''}
                        </div>
                    `;
                })
                .catch(err => {
                    previewContainer.innerHTML = '<p style="color: var(--danger);">Failed to load measurement data.</p>';
                });
        });
    }

    // Unit toggle labels helper in add/edit measurement
    const unitSelect = document.getElementById('measurement_unit');
    const unitIndicators = document.querySelectorAll('.unit-indicator');
    if (unitSelect && unitIndicators.length) {
        unitSelect.addEventListener('change', function() {
            const u = this.value === 'cm' ? 'cm' : 'in';
            unitIndicators.forEach(span => span.textContent = u);
        });
    }
});
