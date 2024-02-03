document.addEventListener("DOMContentLoaded", function() {

    var form = document.querySelector('form[action="/report_issue"]');
    var errorMessage = document.querySelector('.error-message');

    if (form) {
        form.addEventListener('submit', function(event) {
            var issueIdInput = document.getElementById('issue_id');
            var issueDescription = document.getElementById('issue-description').value.trim();

            var issueIdExistsAndEmpty = issueIdInput && !issueIdInput.value.trim();
            var issueDescriptionEmpty = !issueDescription;

            if (issueIdExistsAndEmpty && issueDescriptionEmpty) {
                event.preventDefault();
                errorMessage.style.display = 'block';
                errorMessage.textContent = 'Please include a case number or a description.';
                return false;
            }
        });
    }

    const issueId = document.querySelectorAll('.issue_id');

    issueId.forEach(function(field) {
        field.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });

});

$(document).ready(function() {
    $('.report-issue-reset-password-btn').click(function() {
        $('#forgotten-password-box').toggle();
    });
});