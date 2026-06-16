document.addEventListener("DOMContentLoaded", function () {



    console.log("JS LOADED");

    const sizeButtons = document.querySelectorAll(".sizes button");
    const selectedSize = document.getElementById("selectedSize");

    if (sizeButtons.length > 0) {
        sizeButtons[0].classList.add("active");
    }

    sizeButtons.forEach(button => {

        button.addEventListener("click", function () {

            sizeButtons.forEach(btn => {
                btn.classList.remove("active");
            });

            this.classList.add("active");

            selectedSize.value = this.innerText;

        });

    });

});