/* Study-abroad application form ([data-abroad-application]) on the abroad page.
   - Submits over fetch, shows the server's field errors inline, swaps to a thank-you panel.
   - Each <select> gets a custom listbox dropdown (the native select stays in the form, so
     submitting, resetting and the no-JS fallback keep working).
   - The navbar link "Xaricdə təhsil müraciəti" scrolls to the form and focuses it. */
(function () {
    "use strict";

    var SECTION_ID = "abroad-application";
    var uid = 0;

    /* ------------------------------------------------------------ custom select */
    function enhanceSelect(select) {
        var id = select.id || ("abroad-select-" + (++uid));
        var field = select.closest(".abroad-apply__field");
        var label = field && field.querySelector("label[for='" + id + "']");
        var placeholder = select.options.length && select.options[0].value === "" ? select.options[0].text : "";

        var wrap = document.createElement("div");
        wrap.className = "abroad-select";
        var button = document.createElement("button");
        button.type = "button";
        button.id = id + "-button";
        button.className = "abroad-select__button";
        button.setAttribute("aria-haspopup", "listbox");
        button.setAttribute("aria-expanded", "false");
        var valueEl = document.createElement("span");
        valueEl.className = "abroad-select__value";
        var chevron = document.createElement("span");
        chevron.className = "abroad-select__chevron";
        chevron.setAttribute("aria-hidden", "true");
        button.appendChild(valueEl);
        button.appendChild(chevron);

        var list = document.createElement("ul");
        list.className = "abroad-select__list";
        list.id = id + "-listbox";
        list.setAttribute("role", "listbox");
        list.tabIndex = -1;
        button.setAttribute("aria-controls", list.id);
        if (label) {
            label.id = label.id || (id + "-label");
            label.htmlFor = button.id;
            button.setAttribute("aria-labelledby", label.id + " " + button.id);
            list.setAttribute("aria-labelledby", label.id);
        }

        var items = [];
        Array.prototype.forEach.call(select.options, function (opt) {
            if (opt.value === "") return;
            var li = document.createElement("li");
            li.className = "abroad-select__option";
            li.id = id + "-opt-" + items.length;
            li.setAttribute("role", "option");
            li.dataset.value = opt.value;
            li.textContent = opt.text;
            list.appendChild(li);
            items.push(li);
        });

        wrap.appendChild(button);
        wrap.appendChild(list);
        select.insertAdjacentElement("afterend", wrap);
        select.classList.add("abroad-select__native");
        select.tabIndex = -1;
        select.setAttribute("aria-hidden", "true");
        select._abroadFocus = function () { button.focus(); };

        var active = -1;

        function sync() {
            var chosen = select.value;
            valueEl.textContent = chosen ? select.options[select.selectedIndex].text : placeholder;
            wrap.classList.toggle("is-empty", !chosen);
            items.forEach(function (li) {
                var on = li.dataset.value === chosen;
                li.setAttribute("aria-selected", on ? "true" : "false");
                li.classList.toggle("is-selected", on);
            });
        }

        function setActive(i) {
            if (!items.length) return;
            active = Math.max(0, Math.min(items.length - 1, i));
            items.forEach(function (li, k) { li.classList.toggle("is-active", k === active); });
            list.setAttribute("aria-activedescendant", items[active].id);
            var li = items[active];
            if (li.offsetTop < list.scrollTop) list.scrollTop = li.offsetTop;
            else if (li.offsetTop + li.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = li.offsetTop + li.offsetHeight - list.clientHeight;
        }

        function open() {
            if (wrap.classList.contains("is-open")) return;
            closeAll(wrap);
            /* open upwards when there is not enough room below */
            var rect = button.getBoundingClientRect();
            wrap.classList.toggle("is-up", window.innerHeight - rect.bottom < 280 && rect.top > window.innerHeight - rect.bottom);
            wrap.classList.add("is-open");
            button.setAttribute("aria-expanded", "true");
            var sel = items.findIndex(function (li) { return li.dataset.value === select.value; });
            setActive(sel >= 0 ? sel : 0);
            list.focus({ preventScroll: true });
        }

        function close(refocus) {
            if (!wrap.classList.contains("is-open")) return;
            wrap.classList.remove("is-open");
            button.setAttribute("aria-expanded", "false");
            list.removeAttribute("aria-activedescendant");
            if (refocus) button.focus({ preventScroll: true });
        }
        wrap._close = close;

        function choose(i) {
            if (i < 0 || !items[i]) return;
            select.value = items[i].dataset.value;
            select.dispatchEvent(new Event("change", { bubbles: true }));
            sync();
            close(true);
        }

        button.addEventListener("click", function () {
            if (wrap.classList.contains("is-open")) close(true); else open();
        });
        button.addEventListener("keydown", function (e) {
            if (e.key === "ArrowDown" || e.key === "ArrowUp" || e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                open();
            }
        });
        list.addEventListener("click", function (e) {
            var li = e.target.closest(".abroad-select__option");
            if (li) choose(items.indexOf(li));
        });
        list.addEventListener("mousemove", function (e) {
            var li = e.target.closest(".abroad-select__option");
            if (li && items.indexOf(li) !== active) setActive(items.indexOf(li));
        });

        var typed = "", typedTimer = null;
        list.addEventListener("keydown", function (e) {
            switch (e.key) {
                case "ArrowDown": e.preventDefault(); setActive(active + 1); break;
                case "ArrowUp": e.preventDefault(); setActive(active - 1); break;
                case "Home": e.preventDefault(); setActive(0); break;
                case "End": e.preventDefault(); setActive(items.length - 1); break;
                case "Enter":
                case " ": e.preventDefault(); choose(active); break;
                case "Escape": e.preventDefault(); close(true); break;
                case "Tab": close(false); break;
                default:
                    if (e.key.length === 1) {   /* type-ahead */
                        typed += e.key.toLowerCase();
                        clearTimeout(typedTimer);
                        typedTimer = setTimeout(function () { typed = ""; }, 600);
                        var hit = items.findIndex(function (li) { return li.textContent.toLowerCase().indexOf(typed) === 0; });
                        if (hit >= 0) setActive(hit);
                    }
            }
        });
        list.addEventListener("blur", function (e) {
            if (!wrap.contains(e.relatedTarget)) close(false);
        });

        select.form && select.form.addEventListener("reset", function () { setTimeout(sync, 0); });
        select.addEventListener("change", sync);
        sync();
    }

    function closeAll(except) {
        document.querySelectorAll(".abroad-select.is-open").forEach(function (w) {
            if (w !== except && w._close) w._close(false);
        });
    }

    document.addEventListener("pointerdown", function (e) {
        if (!e.target.closest(".abroad-select")) closeAll(null);
    });

    /* ------------------------------------------------------------ form submit */
    function init(form) {
        var card = form.closest("[data-abroad-application-card]") || form.parentElement;
        var alertEl = card.querySelector("[data-form-alert]");
        var success = card.querySelector("[data-form-success]");
        var submit = form.querySelector("[type=submit]");
        var networkError = form.getAttribute("data-network-error") || "Network error. Please try again.";

        form.querySelectorAll("select").forEach(enhanceSelect);

        form.addEventListener("input", function (e) {
            var field = e.target.closest(".abroad-apply__field");
            if (field) clearError(field);
        });
        form.addEventListener("change", function (e) {
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
                focusFirst(form);
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
                if (first) {
                    if (first._abroadFocus) first._abroadFocus(); else first.focus();
                }
            }).catch(function () {
                showAlert("danger", networkError);
            }).then(function () {
                submit.disabled = false;
            });
        });
    }

    /* ------------------------------------------------------------ jump to the form */
    function focusFirst(form) {
        var first = form.querySelector("input:not([type=hidden]), textarea");
        if (first) first.focus({ preventScroll: true });
    }

    /* Lazy images above the form load while we scroll and push it down the page, so for a
       moment after the jump keep its top edge at its scroll-margin. Any wheel, touch or key
       from the user ends the correction immediately. */
    function keepAligned(section, delay, duration) {
        var target = parseFloat(getComputedStyle(section).scrollMarginTop) || 0;
        var stopAt = performance.now() + delay + duration;
        var startAt = performance.now() + delay;
        var stopped = false;
        function stop() { stopped = true; }
        ["wheel", "touchstart", "keydown"].forEach(function (t) { window.addEventListener(t, stop, { once: true, passive: true }); });
        (function tick(now) {
            if (stopped || now > stopAt) return;
            if (now >= startAt) {
                var diff = section.getBoundingClientRect().top - target;
                if (Math.abs(diff) > 2) window.scrollBy({ top: diff, behavior: "instant" });
            }
            requestAnimationFrame(tick);
        })(performance.now());
    }

    function goToForm(smooth) {
        var section = document.getElementById(SECTION_ID);
        if (!section) return;
        /* one column (phones, tablets): the intro and illustration sit above the form, so
           land on the form card itself */
        var target = section;
        var card = section.querySelector("[data-abroad-application-card]");
        if (card && card.getBoundingClientRect().top - section.getBoundingClientRect().top > 240) target = card;
        /* "instant" overrides the page-wide scroll-behavior: smooth for the arrival jump */
        target.scrollIntoView({ behavior: smooth ? "smooth" : "instant", block: "start" });
        keepAligned(target, smooth ? 900 : 0, 1500);
        /* focus the first field with a mouse only; on touch it would pop the keyboard open */
        var form = section.querySelector("form[data-abroad-application]");
        if (form && !form.hidden && window.matchMedia("(pointer: fine)").matches) focusFirst(form);
    }

    function start() {
        document.querySelectorAll("form[data-abroad-application]").forEach(init);

        /* already on the abroad page: close the menu and glide down instead of reloading */
        document.querySelectorAll("[data-abroad-apply-link]").forEach(function (link) {
            link.addEventListener("click", function (e) {
                if (!document.getElementById(SECTION_ID)) return;
                e.preventDefault();
                var collapse = link.closest(".navbar-collapse.show");
                if (collapse && window.bootstrap && window.bootstrap.Collapse) window.bootstrap.Collapse.getOrCreateInstance(collapse).hide();
                var dropdown = link.closest(".dropdown-menu.show");
                if (dropdown) dropdown.classList.remove("show");
                if (history.replaceState) history.replaceState(null, "", "#" + SECTION_ID);
                goToForm(true);
            });
        });

        /* arriving from another page with #abroad-application: re-align once the layout
           has settled (images and reveals above the form shift it while loading) */
        if (location.hash === "#" + SECTION_ID) {
            var settle = function () { goToForm(false); };
            if (document.readyState === "complete") settle(); else window.addEventListener("load", settle);
        }
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
})();
