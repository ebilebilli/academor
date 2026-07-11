(function () {
    "use strict";

    function boot() {
        var payModalEl = document.getElementById("homeMockPayModal");
        if (!payModalEl || payModalEl.dataset.homeMockPayInit === "1") {
            return;
        }
        payModalEl.dataset.homeMockPayInit = "1";

        if (payModalEl.parentElement !== document.body) {
            document.body.appendChild(payModalEl);
        }

        var form = document.getElementById("home-mock-pay-form");
        var modalAlertEl = document.getElementById("home-mock-pay-modal-alert");
        var modalPackageEl = document.getElementById("home-mock-pay-modal-package");
        var submitBtn = document.getElementById("home-mock-pay-submit");
        var packageHidden = form && form.querySelector('[name="price_package_id"]');
        var contractNumberHidden = form && form.querySelector('[name="contract_number"]');
        var acceptContractEl = form && form.querySelector('[name="accept_contract"]');
        var buyerNameEl = form && form.querySelector('[name="buyer_name"]');
        var buyerPhoneEl = form && form.querySelector('[name="buyer_phone"]');
        var contractBodyEl = document.getElementById("home-mock-pay-contract-body");
        var contractPanelEl = document.getElementById("home-mock-pay-contract-panel");
        var contractTemplatesEl = document.getElementById("home-mock-pay-contract-templates");
        var submitLabel =
            submitBtn && submitBtn.querySelector(".course-pay-modal__submit-label");
        var defaultSubmitText = submitLabel ? submitLabel.textContent : "";
        var payModalInstance = null;
        var activePackageId = null;

        function getPayModal() {
            if (!payModalEl || !window.bootstrap || !bootstrap.Modal) {
                return null;
            }
            if (!payModalInstance) {
                payModalInstance = bootstrap.Modal.getOrCreateInstance(payModalEl);
            }
            return payModalInstance;
        }

        function showAlert(kind, text) {
            if (!modalAlertEl) {
                return;
            }
            modalAlertEl.className = "alert alert-" + kind + " py-2 small mb-3";
            modalAlertEl.textContent = text;
            modalAlertEl.classList.remove("d-none");
        }

        function hideAlert() {
            if (!modalAlertEl) {
                return;
            }
            modalAlertEl.classList.add("d-none");
            modalAlertEl.textContent = "";
        }

        function clearFieldErrors() {
            if (!form) {
                return;
            }
            form.querySelectorAll(".js-field-error").forEach(function (node) {
                if (!node.hasAttribute("data-server-error")) {
                    node.remove();
                }
            });
            form.querySelectorAll(".course-pay-modal__field").forEach(function (wrap) {
                wrap.classList.remove("is-invalid");
            });
        }

        function setFieldError(fieldName, message) {
            if (!form) {
                return;
            }
            var input = form.querySelector('[name="' + fieldName + '"]');
            if (!input) {
                return;
            }
            var wrap = input.closest(".course-pay-modal__field");
            if (!wrap) {
                return;
            }
            wrap.classList.add("is-invalid");
            var errNode = document.createElement("div");
            errNode.className = "text-danger small mt-1 js-field-error";
            errNode.textContent = message;
            wrap.appendChild(errNode);
        }

        function getContractCollapse() {
            if (!contractPanelEl || !window.bootstrap || !bootstrap.Collapse) {
                return null;
            }
            return bootstrap.Collapse.getOrCreateInstance(contractPanelEl, {
                toggle: false,
            });
        }

        function collapseContractPanel() {
            var collapse = getContractCollapse();
            if (collapse) {
                collapse.hide();
            }
        }

        function expandContractPanel() {
            var collapse = getContractCollapse();
            if (collapse) {
                collapse.show();
            }
        }

        function resetAcceptContract() {
            if (acceptContractEl) {
                acceptContractEl.checked = false;
            }
            collapseContractPanel();
        }

        function updateContractBuyerPreview() {
            if (!contractBodyEl) {
                return;
            }
            var name = buyerNameEl ? buyerNameEl.value.trim() : "";
            var phone = buyerPhoneEl ? buyerPhoneEl.value.trim() : "";
            var nameNode = contractBodyEl.querySelector("[data-contract-buyer-name]");
            var phoneNode = contractBodyEl.querySelector("[data-contract-buyer-phone]");
            if (nameNode) {
                nameNode.textContent = name || "—";
            }
            if (phoneNode) {
                phoneNode.textContent = phone || "—";
            }
        }

        function syncContractBody(packageId) {
            if (!contractBodyEl || !contractTemplatesEl || !packageId) {
                return;
            }
            var tpl = contractTemplatesEl.querySelector(
                '[data-contract-package-id="' + packageId + '"]'
            );
            if (!tpl) {
                contractBodyEl.innerHTML = "";
                return;
            }
            contractBodyEl.innerHTML = tpl.innerHTML;
            var contractNumEl = contractBodyEl.querySelector("[data-contract-number]");
            if (contractNumEl && contractNumberHidden) {
                contractNumberHidden.value =
                    contractNumEl.getAttribute("data-contract-number") || "";
            }
            updateContractBuyerPreview();
        }

        function updateModalPackageLabel(name, price) {
            if (!modalPackageEl) {
                return;
            }
            modalPackageEl.textContent =
                (name || "") + (price ? " — " + price + " AZN" : "");
            modalPackageEl.hidden = !modalPackageEl.textContent;
        }

        function openPayModal() {
            var modal = getPayModal();
            if (modal) {
                modal.show();
            }
        }

        function setLoading(loading) {
            if (!submitBtn) {
                return;
            }
            submitBtn.disabled = loading;
            submitBtn.classList.toggle("is-loading", loading);
            submitBtn.setAttribute("aria-busy", loading ? "true" : "false");
            if (submitLabel) {
                submitLabel.textContent = loading
                    ? (form && form.getAttribute("data-msg-redirecting")) || "…"
                    : defaultSubmitText;
            }
        }

        function openForPackage(btn) {
            if (!form || !btn) {
                return;
            }
            var packageId = btn.getAttribute("data-package-id");
            var paymentUrl = btn.getAttribute("data-payment-url");
            if (!packageId || !paymentUrl) {
                return;
            }
            hideAlert();
            clearFieldErrors();
            activePackageId = packageId;
            form.action = paymentUrl;
            if (packageHidden) {
                packageHidden.value = packageId;
            }
            updateModalPackageLabel(
                btn.getAttribute("data-package-name"),
                btn.getAttribute("data-package-price")
            );
            syncContractBody(packageId);
            resetAcceptContract();
            openPayModal();
        }

        document.addEventListener("click", function (e) {
            var btn = e.target.closest("[data-home-mock-pay-open]");
            if (!btn) {
                return;
            }
            e.preventDefault();
            openForPackage(btn);
        });

        if (payModalEl) {
            payModalEl.addEventListener("hidden.bs.modal", function () {
                hideAlert();
                clearFieldErrors();
                setLoading(false);
                collapseContractPanel();
            });
            payModalEl.addEventListener("shown.bs.modal", function () {
                syncContractBody(activePackageId);
                var first = form && form.querySelector('input:not([type="hidden"])');
                if (first) {
                    first.focus();
                }
            });
        }

        if (contractPanelEl) {
            contractPanelEl.addEventListener("shown.bs.collapse", updateContractBuyerPreview);
        }

        if (buyerNameEl) {
            buyerNameEl.addEventListener("input", updateContractBuyerPreview);
        }
        if (buyerPhoneEl) {
            buyerPhoneEl.addEventListener("input", updateContractBuyerPreview);
        }

        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                hideAlert();
                clearFieldErrors();

                if (!packageHidden || !packageHidden.value) {
                    showAlert(
                        "danger",
                        form.getAttribute("data-msg-select-package") ||
                            form.getAttribute("data-msg-generic") ||
                            "Please select a package."
                    );
                    return;
                }

                if (acceptContractEl && !acceptContractEl.checked) {
                    expandContractPanel();
                }

                var fd = new FormData(form);
                var token = form.querySelector("[name=csrfmiddlewaretoken]");
                setLoading(true);

                fetch(form.action, {
                    method: "POST",
                    body: fd,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": token ? token.value : "",
                    },
                    credentials: "same-origin",
                })
                    .then(function (response) {
                        return response.text().then(function (text) {
                            var data = null;
                            try {
                                data = text ? JSON.parse(text) : null;
                            } catch (parseErr) {
                                data = null;
                            }
                            return { ok: response.ok, data: data };
                        });
                    })
                    .then(function (res) {
                        if (res.data && res.data.success && res.data.redirect_url) {
                            window.location.href = res.data.redirect_url;
                            return;
                        }

                        if (!res.data) {
                            showAlert(
                                "danger",
                                form.getAttribute("data-msg-network") || "Network error."
                            );
                            setLoading(false);
                            return;
                        }

                        var msg = res.data.message || "";
                        if (
                            !msg &&
                            res.data.errors &&
                            res.data.errors.__all__ &&
                            res.data.errors.__all__[0]
                        ) {
                            msg = res.data.errors.__all__[0];
                        }
                        if (res.data.errors) {
                            if (
                                res.data.errors.accept_contract &&
                                res.data.errors.accept_contract[0]
                            ) {
                                expandContractPanel();
                            }
                            Object.keys(res.data.errors).forEach(function (field) {
                                if (field === "__all__") {
                                    return;
                                }
                                var list = res.data.errors[field];
                                if (list && list[0]) {
                                    setFieldError(field, list[0]);
                                }
                            });
                        }
                        if (!msg) {
                            msg =
                                form.getAttribute("data-msg-generic") ||
                                "Please correct the errors in the form.";
                        }
                        showAlert("danger", msg);
                        setLoading(false);
                    })
                    .catch(function () {
                        showAlert(
                            "danger",
                            form.getAttribute("data-msg-network") || "Network error."
                        );
                        setLoading(false);
                    });
            });
        }

        if (payModalEl.getAttribute("data-open-on-load") === "true") {
            var initialId = payModalEl.getAttribute("data-initial-package-id");
            var trigger = initialId
                ? document.querySelector(
                      '[data-home-mock-pay-open][data-package-id="' + initialId + '"]'
                  )
                : document.querySelector("[data-home-mock-pay-open]");
            if (trigger) {
                openForPackage(trigger);
            }
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
