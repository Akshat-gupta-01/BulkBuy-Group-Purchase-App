document.addEventListener('DOMContentLoaded', () => {
    // Auto-focus quantity input after selecting product
    const productSelect = document.querySelector('select[name="product_id"]');
    const qtyInput = document.querySelector('input[name="quantity"]');
    if (productSelect && qtyInput) {
        productSelect.addEventListener('change', () => {
            qtyInput.focus();
        });
    }

    // Confirm logout
    const logoutLink = document.querySelector('a.logout');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            if (!confirm("Are you sure you want to log out?")) {
                e.preventDefault();
            }
        });
    }
});
