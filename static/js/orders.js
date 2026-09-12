// Orders Creation & Management Helpers
document.addEventListener('DOMContentLoaded', function() {
    // Delivery method toggle
    const deliverySelect = document.getElementById('delivery_method');
    const addressGroup = document.getElementById('delivery_address_group');

    if (deliverySelect && addressGroup) {
        const toggleAddress = () => {
            if (deliverySelect.value === 'delivery') {
                addressGroup.style.display = 'block';
            } else {
                addressGroup.style.display = 'none';
            }
        };
        deliverySelect.addEventListener('change', toggleAddress);
        toggleAddress();
    }

    // Reference image upload preview
    const imageInput = document.getElementById('reference_image');
    const imagePreview = document.getElementById('image_preview');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    imagePreview.src = evt.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Set min date to today for expected completion date
    const dateInput = document.getElementById('expected_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }
});
