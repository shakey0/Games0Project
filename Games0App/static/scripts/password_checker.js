function checkPasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthElement = document.getElementById('password-strength');

    const lowercaseRegex = /[a-z]/;
    const uppercaseRegex = /[A-Z]/;
    const digitRegex = /[0-9]/;
    const symbolRegex = /[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]/;

    let strengthLevel = 0;
    let message = '';
    let strength_ = 'Strength: ';

    if (password.length === 0) {
        strengthLevel = 0;
        strength_ = '';
    } else if (password.length < 8) {
        strengthLevel = 1;
    } else if (password.length >= 8) {
        strengthLevel = 0;
        if (lowercaseRegex.test(password)) strengthLevel++;
        if (uppercaseRegex.test(password)) strengthLevel++;
        if (digitRegex.test(password)) strengthLevel++;
        if (symbolRegex.test(password)) strengthLevel++;
    }
    if (password.length >= 12) {
        strengthLevel++;
    }

    const strengthLevels = ['', 'Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'];
    message = strength_ + strengthLevels[strengthLevel];
    strengthElement.textContent = message;
}