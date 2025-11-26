
  const togglePassword = document.querySelector("#togglePassword");
  const password = document.querySelector("#passwordInput");

  togglePassword.addEventListener("click", function () {
    const type =
      password.getAttribute("type") === "password" ? "text" : "password";
    password.setAttribute("type", type);

    this.textContent = type === "password" ? "visibility" : "visibility_off";
  });
