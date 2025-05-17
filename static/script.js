document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".form-box.login form");

    if (!form) return; // Prevent errors if form does not exist

    const usernameInput = form.querySelector("input[type='text']");
    const emailInput = form.querySelector("input[type='email']");
    const passwordInput = form.querySelector("input[type='password']");
    const termsCheckbox = form.querySelector("input[type='checkbox']");

    const errorMessages = {
        username: "Username cannot be empty.",
        email: "Please enter a valid email address.",
        password: "Password must be at least 6 characters long.",
        terms: "You must agree to the terms and conditions."
    };

    function showError(input, message) {
        clearError(input);
        let errorElement = document.createElement("span");
        errorElement.classList.add("error-message");
        errorElement.textContent = message;
        input.parentNode.appendChild(errorElement);
    }

    function clearError(input) {
        let errorElement = input.parentNode.querySelector(".error-message");
        if (errorElement) {
            errorElement.remove();
        }
    }

    form.addEventListener("submit", function (event) {
        let isValid = true;

        if (usernameInput.value.trim() === "") {
            showError(usernameInput, errorMessages.username);
            isValid = false;
        } else {
            clearError(usernameInput);
        }

        const emailValue = emailInput.value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailValue)) {
            showError(emailInput, errorMessages.email);
            isValid = false;
        } else {
            clearError(emailInput);
        }

        if (passwordInput.value.trim().length < 6) {
            showError(passwordInput, errorMessages.password);
            isValid = false;
        } else {
            clearError(passwordInput);
        }

        if (!termsCheckbox.checked) {
            showError(termsCheckbox, errorMessages.terms);
            isValid = false;
        } else {
            clearError(termsCheckbox);
        }

        if (!isValid) {
            event.preventDefault(); // Prevent form submission if invalid
        }
    });

    const iconClose = document.querySelector('.icon-close');
    if (iconClose) {
        const redirectUrl = iconClose.dataset.redirectUrl;
        iconClose.addEventListener('click', () => {
            window.location.href = redirectUrl;
        });
    }
});
