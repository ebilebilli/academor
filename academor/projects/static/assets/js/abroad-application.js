/* Study-abroad application forms ([data-abroad-application]): submit over fetch, show the
   server's field errors inline, reset on success. Without JS the form posts normally. */
(function () {
    "use strict";

    function markEmptySelects(form) {
        form.querySelectorAll("select").forEach(function (sel) {
            sel.classList.toggle("is-empty", !sel.value);
        });
    }

    function init(form) {
        var card = form.closest("[data-abroad-application-card]") || form.parentElement;
        var alertEl = card.querySelector("[data-form-alert]");
        var success = card.querySelector("[data-form-success]");
        var submit = form.querySelector("[type=submit]");
        var networkError = form.getAttribute("data-network-error") || "Network error. Please try again.";

        markEmptySelects(form);
        form.addEventListener("change", function (e) {
            if (e.target.tagName === "SELECT") e.target.classList.toggle("is-empty", !e.target.value);
            var field = e.target.closest(".abroad-apply__field");
            if (field) clearError(field);
        });

        function showAlert(kind, text) {
            if (!alertEl) return;
            alertEl.className = "alert alert-" + kind;
            alertEl.textContent = text;
        }

        function clearError(field) {
            field.classList.remove("has-error");
            var err = field.querySelector("[data-field-error]");
            if (err) err.textContent = "";
            var input = field.querySelector("input, select, textarea");
            if (input) input.removeAttribute("aria-invalid");
        }

        var again = success && success.querySelector("[data-form-again]");
        if (again) {
            again.addEventListener("click", function () {
                success.hidden = true;
                form.hidden = false;
                var first = form.querySelector("input:not([type=hidden]), select, textarea");
                if (first) first.focus();
            });
        }

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            form.querySelectorAll(".abroad-apply__field").forEach(clearError);
            if (alertEl) alertEl.className = "alert d-none";
            submit.disabled = true;

            fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin"
            }).then(function (r) {
                return r.json().catch(function () { return null; });
            }).then(function (data) {
                if (data && data.success) {
                    form.reset();
                    markEmptySelects(form);
                    var ts = form.querySelector(".cf-turnstile");
                    if (window.turnstile && ts) { try { window.turnstile.reset(ts); } catch (err) { /* ignore */ } }
                    if (success) {
                        /* swap the form for a thank-you panel; "new application" brings it back */
                        success.querySelector("[data-form-success-text]").textContent = data.message || "";
                        form.hidden = true;
                        success.hidden = false;
                        success.focus({ preventScroll: true });
                    } else {
                        showAlert("success", data.message || "");
                    }
                    return;
                }
                var msg = (data && data.message) || networkError;
                var errors = (data && data.errors) || {};
                if (errors.__all__ && errors.__all__[0]) msg = errors.__all__[0];
                showAlert("danger", msg);
                var first = null;
                Object.keys(errors).forEach(function (name) {
                    var input = form.querySelector("[name='" + name + "']");
                    var field = input && input.closest(".abroad-apply__field");
                    if (!field) return;
                    field.classList.add("has-error");
                    input.setAttribute("aria-invalid", "true");
                    var err = field.querySelector("[data-field-error]");
                    if (err) err.textContent = errors[name][0] || "";
                    if (!first) first = input;
                });
                if (first) first.focus({ preventScroll: false });
            }).catch(function () {
                showAlert("danger", networkError);
            }).then(function () {
                submit.disabled = false;
            });
        });
    }

    function start() {
        document.querySelectorAll("form[data-abroad-application]").forEach(init);
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
})();
