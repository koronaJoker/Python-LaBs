function activateFlashModal() {
    const modal = document.querySelector(".modal");
    if (!modal) {
        return;
    }

    const closeButton = modal.querySelector(".modal__close");
    const overlay = modal.querySelector(".modal__overlay");

    function hide() {
        modal.classList.remove("modal--open");
    }

    if (closeButton) {
        closeButton.addEventListener("click", hide);
    }
    if (overlay) {
        overlay.addEventListener("click", hide);
    }
}

function activateMobileMenu() {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".site-nav");
    if (!toggle || !nav) {
        return;
    }

    toggle.addEventListener("click", () => {
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!isExpanded));
        nav.classList.toggle("site-nav--open");
    });
}

document.addEventListener("DOMContentLoaded", () => {
    activateFlashModal();
    activateMobileMenu();
});