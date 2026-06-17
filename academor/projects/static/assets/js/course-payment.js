(function () {
    function boot() {
        var root = document.getElementById('course-pay');
        if (!root) {
            return;
        }

        var packagesEl = root.querySelector('[data-course-pay-packages]');
        var payModalEl = document.getElementById('coursePayModal');
        var form = document.getElementById('course-pay-form');
        var sectionAlertEl = document.getElementById('course-pay-alert');
        var modalAlertEl = document.getElementById('course-pay-modal-alert');
        var modalPackageEl = document.getElementById('course-pay-modal-package');
        var submitBtn = document.getElementById('course-pay-submit');
        var packageHidden = document.getElementById('id_price_package_id');
        var contractNumberHidden = document.getElementById('id_contract_number');
        var contractBodyEl = document.getElementById('course-pay-contract-body');
        var contractPanelEl = document.getElementById('course-pay-contract-panel');
        var contractToggleEl = document.getElementById('course-pay-contract-toggle');
        var contractTemplatesEl = document.getElementById(
            'course-pay-contract-templates'
        );
        var acceptContractEl = document.getElementById('id_accept_contract');
        var buyerNameEl = document.getElementById('id_buyer_name');
        var buyerPhoneEl = document.getElementById('id_buyer_phone');
        var submitLabel =
            submitBtn && submitBtn.querySelector('.course-pay-modal__submit-label');
        var defaultSubmitText = submitLabel ? submitLabel.textContent : '';
        var payModalInstance = null;

        if (payModalEl && payModalEl.parentElement !== document.body) {
            document.body.appendChild(payModalEl);
        }

        function getPayModal() {
            if (!payModalEl || !window.bootstrap || !bootstrap.Modal) {
                return null;
            }
            if (!payModalInstance) {
                payModalInstance = bootstrap.Modal.getOrCreateInstance(payModalEl);
            }
            return payModalInstance;
        }

        var defaultIndex = parseInt(
            root.getAttribute('data-default-index') ||
                (root.querySelector('[data-default-index]') &&
                    root.querySelector('[data-default-index]').getAttribute(
                        'data-default-index'
                    )) ||
                '0',
            10
        );
        if (isNaN(defaultIndex) || defaultIndex < 0) {
            defaultIndex = 0;
        }

        var items = packagesEl
            ? Array.prototype.slice.call(
                  packagesEl.querySelectorAll('[data-package-item]')
              )
            : [];
        var n = items.length;
        var logicalIndex = 0;

        function showAlert(kind, text, target) {
            var el = target === 'section' ? sectionAlertEl : modalAlertEl;
            if (!el) {
                return;
            }
            el.className = 'alert alert-' + kind + ' py-2 small mb-3';
            el.textContent = text;
            el.classList.remove('d-none');
        }

        function hideAlert(target) {
            if (!target || target === 'section') {
                if (sectionAlertEl) {
                    sectionAlertEl.classList.add('d-none');
                    sectionAlertEl.textContent = '';
                }
            }
            if (!target || target === 'modal') {
                if (modalAlertEl) {
                    modalAlertEl.classList.add('d-none');
                    modalAlertEl.textContent = '';
                }
            }
        }

        function hideAllAlerts() {
            hideAlert('section');
            hideAlert('modal');
        }

        function clearFieldErrors() {
            if (!form) {
                return;
            }
            form.querySelectorAll('.js-field-error').forEach(function (node) {
                node.remove();
            });
            form.querySelectorAll('.course-pay-modal__field').forEach(function (wrap) {
                wrap.classList.remove('is-invalid');
            });
            if (packagesEl) {
                packagesEl.classList.remove('is-invalid');
            }
        }

        function setFieldError(fieldName, message) {
            if (!form) {
                return;
            }
            if (fieldName === 'price_package_id' && packagesEl) {
                packagesEl.classList.add('is-invalid');
                return;
            }
            var input = form.querySelector('[name="' + fieldName + '"]');
            if (!input) {
                return;
            }
            var wrap = input.closest('.course-pay-modal__field');
            if (!wrap) {
                return;
            }
            wrap.classList.add('is-invalid');
            var errNode = document.createElement('div');
            errNode.className = 'text-danger small mt-1 js-field-error';
            errNode.textContent = message;
            wrap.appendChild(errNode);
        }

        function getRadio(logical) {
            var item = items[logical];
            if (!item) {
                return null;
            }
            return item.querySelector('.course-pay-card__radio');
        }

        function updateModalPackageLabel() {
            if (!modalPackageEl) {
                return;
            }
            var radio = getRadio(logicalIndex);
            if (!radio) {
                modalPackageEl.hidden = true;
                modalPackageEl.textContent = '';
                return;
            }
            var name = radio.getAttribute('data-name') || '';
            var price = radio.getAttribute('data-price') || '';
            modalPackageEl.textContent =
                name + (price ? ' — ' + price + ' AZN' : '');
            modalPackageEl.hidden = !modalPackageEl.textContent;
        }

        function resetAcceptContract() {
            if (acceptContractEl) {
                acceptContractEl.checked = false;
            }
            collapseContractPanel();
        }

        function getContractCollapse() {
            if (
                !contractPanelEl ||
                !window.bootstrap ||
                !bootstrap.Collapse
            ) {
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

        function updateContractBuyerPreview() {
            if (!contractBodyEl) {
                return;
            }
            var nameTarget = contractBodyEl.querySelector(
                '[data-contract-buyer-name]'
            );
            var phoneTarget = contractBodyEl.querySelector(
                '[data-contract-buyer-phone]'
            );
            var name = buyerNameEl ? buyerNameEl.value.trim() : '';
            var phone = buyerPhoneEl ? buyerPhoneEl.value.trim() : '';
            if (nameTarget) {
                nameTarget.textContent = name || '_______________';
            }
            if (phoneTarget) {
                phoneTarget.textContent = phone || '_______________';
            }
        }

        function syncContractBody() {
            if (!contractBodyEl || !contractTemplatesEl) {
                return;
            }
            var radio = getRadio(logicalIndex);
            if (!radio) {
                return;
            }
            var packageId =
                radio.getAttribute('data-package-id') || radio.value || '';
            var template = contractTemplatesEl.querySelector(
                '[data-contract-package-id="' + packageId + '"]'
            );
            if (!template) {
                return;
            }
            contractBodyEl.innerHTML = template.innerHTML;
            var doc = contractBodyEl.querySelector('[data-contract-number]');
            if (doc && contractNumberHidden) {
                contractNumberHidden.value =
                    doc.getAttribute('data-contract-number') || '';
            }
            updateContractBuyerPreview();
        }

        function openPayModal() {
            var modal = getPayModal();
            if (!modal) {
                return;
            }
            syncSelectedPackage();
            updateModalPackageLabel();
            syncContractBody();
            hideAlert('modal');
            modal.show();
        }

        function closePayModal() {
            var modal = getPayModal();
            if (modal) {
                modal.hide();
            }
        }

        function syncSelectedPackage() {
            var radio = getRadio(logicalIndex);
            if (!radio) {
                return null;
            }
            if (packageHidden) {
                packageHidden.value = radio.value;
            }
            if (packagesEl) {
                packagesEl.classList.remove('is-invalid');
            }
            return radio;
        }

        function updateVisualStates() {
            items.forEach(function (item, i) {
                var card = item.querySelector('[data-package-card]');
                var radio = item.querySelector('.course-pay-card__radio');
                var selected = i === logicalIndex;
                item.setAttribute('aria-selected', selected ? 'true' : 'false');
                if (card) {
                    card.classList.toggle('is-active', selected);
                }
                if (radio) {
                    radio.checked = selected;
                }
            });
        }

        function selectPackage(index, options) {
            options = options || {};
            if (!n) {
                return;
            }
            index = Math.max(0, Math.min(index, n - 1));
            var packageChanged = index !== logicalIndex;
            if (packageChanged && !options.keepModal) {
                closePayModal();
            }
            logicalIndex = index;
            updateVisualStates();
            syncSelectedPackage();
            if (payModalEl && payModalEl.classList.contains('show')) {
                updateModalPackageLabel();
                syncContractBody();
                if (packageChanged) {
                    resetAcceptContract();
                }
            }
        }

        function setLoading(loading) {
            if (!submitBtn) {
                return;
            }
            submitBtn.disabled = loading;
            submitBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
            if (submitLabel) {
                submitLabel.textContent = loading
                    ? (form && form.getAttribute('data-msg-redirecting')) || '…'
                    : defaultSubmitText;
            }
        }

        function initPackages() {
            if (!n) {
                return;
            }
            if (defaultIndex >= n) {
                defaultIndex = 0;
            }
            logicalIndex = defaultIndex;
            updateVisualStates();
            syncSelectedPackage();
            syncContractBody();

            items.forEach(function (item) {
                var card = item.querySelector('[data-package-card]');
                if (!card) {
                    return;
                }
                card.addEventListener('click', function (e) {
                    if (e.target.closest('[data-pay-open]')) {
                        return;
                    }
                    var index = parseInt(
                        item.getAttribute('data-package-index'),
                        10
                    );
                    if (!isNaN(index)) {
                        selectPackage(index);
                    }
                });
                card.addEventListener('keydown', function (e) {
                    var idx = parseInt(
                        item.getAttribute('data-package-index'),
                        10
                    );
                    if (isNaN(idx)) {
                        return;
                    }
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        selectPackage(idx);
                        return;
                    }
                    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                        e.preventDefault();
                        var next = Math.min(logicalIndex + 1, n - 1);
                        if (next !== logicalIndex) {
                            selectPackage(next);
                            var nextCard = items[next].querySelector(
                                '[data-package-card]'
                            );
                            if (nextCard) {
                                nextCard.focus();
                            }
                        }
                        return;
                    }
                    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                        e.preventDefault();
                        var prev = Math.max(logicalIndex - 1, 0);
                        if (prev !== logicalIndex) {
                            selectPackage(prev);
                            var prevCard = items[prev].querySelector(
                                '[data-package-card]'
                            );
                            if (prevCard) {
                                prevCard.focus();
                            }
                        }
                    }
                });
            });
        }

        root.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-pay-open]');
            if (!btn) {
                return;
            }
            e.preventDefault();
            e.stopPropagation();
            var item = btn.closest('[data-package-item]');
            if (item) {
                var index = parseInt(
                    item.getAttribute('data-package-index'),
                    10
                );
                if (!isNaN(index)) {
                    selectPackage(index, { keepModal: true });
                }
            }
            openPayModal();
            btn.blur();
        });

        if (payModalEl) {
            payModalEl.addEventListener('hidden.bs.modal', function () {
                hideAlert('modal');
                clearFieldErrors();
                setLoading(false);
                collapseContractPanel();
            });
            payModalEl.addEventListener('shown.bs.modal', function () {
                syncContractBody();
                var first = form && form.querySelector('input:not([type="hidden"])');
                if (first) {
                    first.focus();
                }
            });
        }

        initPackages();

        if (
            payModalEl &&
            payModalEl.getAttribute('data-open-on-load') === 'true'
        ) {
            openPayModal();
        }

        window.addEventListener('pageshow', function (evt) {
            if (evt && evt.persisted) {
                setLoading(false);
                hideAllAlerts();
                clearFieldErrors();
                selectPackage(logicalIndex, { keepModal: true });
            }
        });

        if (contractPanelEl) {
            contractPanelEl.addEventListener(
                'shown.bs.collapse',
                updateContractBuyerPreview
            );
        }

        if (form) {
            if (buyerNameEl) {
                buyerNameEl.addEventListener('input', updateContractBuyerPreview);
            }
            if (buyerPhoneEl) {
                buyerPhoneEl.addEventListener('input', updateContractBuyerPreview);
            }
        }

        if (!form) {
            return;
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            hideAllAlerts();
            clearFieldErrors();

            if (!syncSelectedPackage()) {
                showAlert(
                    'danger',
                    form.getAttribute('data-msg-select-package') ||
                        'Please select a package.',
                    'modal'
                );
                openPayModal();
                return;
            }

            if (!payModalEl || !payModalEl.classList.contains('show')) {
                openPayModal();
            }

            if (acceptContractEl && !acceptContractEl.checked) {
                expandContractPanel();
            }

            var fd = new FormData(form);
            var token = form.querySelector('[name=csrfmiddlewaretoken]');
            setLoading(true);

            fetch(form.action, {
                method: 'POST',
                body: fd,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token ? token.value : '',
                },
                credentials: 'same-origin',
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
                        openPayModal();
                        showAlert(
                            'danger',
                            form.getAttribute('data-msg-network') ||
                                'Network error.',
                            'modal'
                        );
                        setLoading(false);
                        return;
                    }

                    var msg = res.data.message || '';
                    if (
                        !msg &&
                        res.data.errors &&
                        res.data.errors.__all__ &&
                        res.data.errors.__all__[0]
                    ) {
                        msg = res.data.errors.__all__[0];
                    }
                    if (res.data.errors) {
                        var fields = Object.keys(res.data.errors);
                        if (
                            res.data.errors.accept_contract &&
                            res.data.errors.accept_contract[0]
                        ) {
                            expandContractPanel();
                        }
                        if (!msg && fields.length) {
                            var firstKey = fields[0];
                            if (firstKey !== '__all__') {
                                var first = res.data.errors[firstKey];
                                msg = first && first[0] ? first[0] : msg;
                            }
                        }
                        fields.forEach(function (field) {
                            if (field === '__all__') {
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
                            form.getAttribute('data-msg-generic') ||
                            'Please correct the errors in the form.';
                    }
                    openPayModal();
                    showAlert('danger', msg, 'modal');
                    setLoading(false);
                })
                .catch(function () {
                    openPayModal();
                    showAlert(
                        'danger',
                        form.getAttribute('data-msg-network') ||
                            'Network error.',
                        'modal'
                    );
                    setLoading(false);
                });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
