(function () {
    function boot() {
        var root = document.getElementById('course-pay');
        if (!root) {
            return;
        }

        var tabsEl = root.querySelector('[data-course-pay-tabs]');
        var tabIndicatorEl = tabsEl
            ? tabsEl.querySelector('[data-course-pay-indicator]')
            : null;
        var tabPanelsEl = root.querySelector('[data-course-pay-tab-panels]');
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

        var activeTab = root.getAttribute('data-default-tab') || '';
        var activePanel = null;
        var packagesEl = null;
        var items = [];
        var n = 0;
        var logicalIndex = 0;
        var defaultIndex = 0;

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

        function getActivePanel() {
            if (!tabPanelsEl) {
                return null;
            }
            return tabPanelsEl.querySelector('[data-tab-panel].is-active');
        }

        function refreshActivePanelState() {
            activePanel = getActivePanel();
            packagesEl = activePanel
                ? activePanel.querySelector('[data-course-pay-packages]')
                : null;
            defaultIndex = parseInt(
                (activePanel &&
                    activePanel.getAttribute('data-default-index')) ||
                    root.getAttribute('data-default-index') ||
                    '0',
                10
            );
            if (isNaN(defaultIndex) || defaultIndex < 0) {
                defaultIndex = 0;
            }
            items = packagesEl
                ? Array.prototype.slice.call(
                      packagesEl.querySelectorAll('[data-package-item]')
                  )
                : [];
            n = items.length;
        }

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
                if (!node.hasAttribute('data-server-error')) {
                    node.remove();
                }
            });
            form.querySelectorAll('.course-pay-modal__field').forEach(function (wrap) {
                wrap.classList.remove('is-invalid');
            });
            root.querySelectorAll('[data-course-pay-packages]').forEach(function (el) {
                el.classList.remove('is-invalid');
            });
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
                if (packageHidden) {
                    packageHidden.value = '';
                }
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
            submitBtn.classList.toggle('is-loading', loading);
            submitBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
            if (submitLabel) {
                submitLabel.textContent = loading
                    ? (form && form.getAttribute('data-msg-redirecting')) || '…'
                    : defaultSubmitText;
            }
        }

        function updateTabIndicator() {
            if (!tabsEl || !tabIndicatorEl) {
                return;
            }
            var activeBtn = tabsEl.querySelector('[data-payment-tab].is-active');
            if (!activeBtn) {
                tabIndicatorEl.classList.add('is-hidden');
                return;
            }
            tabIndicatorEl.classList.remove('is-hidden');
            tabIndicatorEl.style.width = activeBtn.offsetWidth + 'px';
            tabIndicatorEl.style.height = activeBtn.offsetHeight + 'px';
            tabIndicatorEl.style.transform =
                'translate3d(' +
                activeBtn.offsetLeft +
                'px,' +
                activeBtn.offsetTop +
                'px,0)';
        }

        function scrollActiveTabIntoView() {
            if (!tabsEl) {
                return;
            }
            var activeBtn = tabsEl.querySelector('[data-payment-tab].is-active');
            if (
                !activeBtn ||
                !window.matchMedia('(max-width: 575.98px)').matches
            ) {
                return;
            }
            activeBtn.scrollIntoView({
                behavior: 'auto',
                block: 'nearest',
                inline: 'center',
            });
        }

        function setActiveTabButton(tabKey) {
            if (!tabsEl) {
                return;
            }
            tabsEl.querySelectorAll('[data-payment-tab]').forEach(function (btn) {
                var isActive = btn.getAttribute('data-payment-tab') === tabKey;
                btn.classList.toggle('is-active', isActive);
                btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });
            window.requestAnimationFrame(function () {
                updateTabIndicator();
            });
            scrollActiveTabIntoView();
        }

        function switchPaymentTab(tabKey) {
            if (!tabKey || tabKey === activeTab || !tabPanelsEl) {
                return;
            }

            hideAllAlerts();
            closePayModal();

            tabPanelsEl.querySelectorAll('[data-tab-panel]').forEach(function (panel) {
                var isActive = panel.getAttribute('data-tab-panel') === tabKey;
                panel.classList.toggle('is-active', isActive);
            });

            activeTab = tabKey;
            setActiveTabButton(tabKey);
            refreshActivePanelState();

            if (!n) {
                logicalIndex = 0;
                syncSelectedPackage();
                return;
            }

            if (defaultIndex >= n) {
                defaultIndex = 0;
            }
            logicalIndex = defaultIndex;
            updateVisualStates();
            syncSelectedPackage();
            syncContractBody();
        }

        function bindPackageInteractions() {
            root.querySelectorAll('[data-package-item]').forEach(function (item) {
                var card = item.querySelector('[data-package-card]');
                if (!card || card.getAttribute('data-bound') === '1') {
                    return;
                }
                card.setAttribute('data-bound', '1');

                card.addEventListener('click', function (e) {
                    if (e.target.closest('[data-pay-open]')) {
                        return;
                    }
                    if (!item.closest('[data-tab-panel].is-active')) {
                        return;
                    }
                    var index = parseInt(
                        item.getAttribute('data-package-index'),
                        10
                    );
                    if (!isNaN(index)) {
                        refreshActivePanelState();
                        selectPackage(index);
                    }
                });

                card.addEventListener('keydown', function (e) {
                    if (!item.closest('[data-tab-panel].is-active')) {
                        return;
                    }
                    var idx = parseInt(
                        item.getAttribute('data-package-index'),
                        10
                    );
                    if (isNaN(idx)) {
                        return;
                    }
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        refreshActivePanelState();
                        selectPackage(idx);
                        return;
                    }
                    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                        e.preventDefault();
                        refreshActivePanelState();
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
                        refreshActivePanelState();
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

        function initPackages() {
            refreshActivePanelState();
            if (!n) {
                logicalIndex = 0;
                syncSelectedPackage();
                return;
            }
            if (defaultIndex >= n) {
                defaultIndex = 0;
            }
            logicalIndex = defaultIndex;
            updateVisualStates();
            syncSelectedPackage();
            syncContractBody();
        }

        if (tabsEl) {
            tabsEl.addEventListener('click', function (e) {
                var btn = e.target.closest('[data-payment-tab]');
                if (!btn) {
                    return;
                }
                switchPaymentTab(btn.getAttribute('data-payment-tab'));
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
                refreshActivePanelState();
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

        bindPackageInteractions();
        initPackages();
        updateTabIndicator();

        window.addEventListener('resize', updateTabIndicator);

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
                refreshActivePanelState();
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
            refreshActivePanelState();

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

        function scrollToPackagesSection() {
            var navbar = document.querySelector('.navbar.sticky-top');
            var offset = navbar ? navbar.offsetHeight + 16 : 96;
            var top =
                root.getBoundingClientRect().top + window.pageYOffset - offset;
            var prefersReducedMotion =
                window.matchMedia &&
                window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({
                top: Math.max(0, top),
                behavior: prefersReducedMotion ? 'auto' : 'smooth',
            });
        }

        function setPackagesCtaVisible(visible) {
            var cta = document.getElementById('course-pay-sticky-cta');
            if (!cta) return;
            cta.classList.toggle('is-visible', visible);
            cta.setAttribute('aria-hidden', visible ? 'false' : 'true');
        }

        function initPackagesStickyCta() {
            var cta = document.getElementById('course-pay-sticky-cta');
            if (!cta) {
                return;
            }

            var jumpBtn = cta.querySelector('[data-course-pay-jump]');
            if (jumpBtn) {
                jumpBtn.addEventListener('click', function () {
                    scrollToPackagesSection();
                });
            }

            function syncCtaVisibility(isPackagesVisible) {
                setPackagesCtaVisible(!isPackagesVisible);
            }

            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(
                    function (entries) {
                        entries.forEach(function (entry) {
                            syncCtaVisibility(entry.isIntersecting);
                        });
                    },
                    {
                        root: null,
                        rootMargin: '-96px 0px 0px 0px',
                        threshold: 0,
                    }
                );
                observer.observe(root);
                return;
            }

            setPackagesCtaVisible(true);
        }

        initPackagesStickyCta();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
