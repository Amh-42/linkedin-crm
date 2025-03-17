// Wait for DOM content to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Auto-focus first input on forms
    var firstInput = document.querySelector('form input:not([type=hidden]):first-child');
    if (firstInput) {
        firstInput.focus();
    }

    // Handle tag input with autocomplete
    var tagInput = document.querySelector('input[name="tags"]');
    if (tagInput) {
        // Example of enhancing the tag input (in a real app, you'd use a proper tag input library)
        tagInput.addEventListener('keydown', function (e) {
            if (e.key === ',') {
                // Prevent comma from being entered (it's used as separator)
                setTimeout(function () {
                    var value = tagInput.value;
                    if (value.endsWith(',')) {
                        tagInput.value = value.replace(/,$/, '') + ', ';
                    }
                }, 0);
            }
        });
    }
}); 