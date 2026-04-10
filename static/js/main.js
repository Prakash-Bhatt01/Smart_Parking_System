document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";

            setTimeout(function() {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        }, 5000);
    });
});

if ("serviceWorker" in navigator) {
    window.addEventListener("load", function() {
        navigator.serviceWorker.register("/sw.js", { scope: "/" })
            .then(function(registration) {
                console.log("SmartPark service worker registered:", registration.scope);
            })
            .catch(function(error) {
                console.log("Service worker registration failed:", error);
            });
    });
}
