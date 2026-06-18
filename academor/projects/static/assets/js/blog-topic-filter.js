(function () {
    function parseTagsFromSearch(search) {
        var params = new URLSearchParams(search || window.location.search);
        return Array.from(params.getAll('tag'))
            .map(function (s) {
                return (s || '').trim();
            })
            .filter(Boolean)
            .sort();
    }

    function buildUrl(basePath, selectedSlugs) {
        var url = new URL(basePath, window.location.origin);
        selectedSlugs.forEach(function (slug) {
            url.searchParams.append('tag', slug);
        });
        return url.pathname + url.search;
    }

    function getSelectedSlugs(root) {
        var selected = [];
        root.querySelectorAll('[data-blog-topic-option]:checked').forEach(function (cb) {
            selected.push(cb.value);
        });
        return selected.sort();
    }

    function syncCheckboxes(root, slugs) {
        root.querySelectorAll('[data-blog-topic-option]').forEach(function (cb) {
            cb.checked = slugs.indexOf(cb.value) !== -1;
        });
    }

    function updateFilterLabel(root, selectedSlugs) {
        var valueEl = root.querySelector('[data-blog-topic-value]');
        var allBtn = root.querySelector('[data-blog-topic-all]');
        if (!valueEl) {
            return;
        }

        var allLabel = root.dataset.i18nAll || 'All';
        var topicsLabel = root.dataset.i18nTopics || 'topics';

        if (selectedSlugs.length === 0) {
            valueEl.textContent = allLabel;
        } else if (selectedSlugs.length === 1) {
            var cb = root.querySelector('[data-blog-topic-option][value="' + selectedSlugs[0] + '"]');
            var textEl = cb && cb.closest('.blog-topic-dropdown__option');
            var nameEl = textEl && textEl.querySelector('.blog-topic-dropdown__option-text');
            valueEl.textContent = nameEl ? nameEl.textContent.trim() : selectedSlugs[0];
        } else {
            valueEl.textContent = selectedSlugs.length + ' ' + topicsLabel;
        }

        if (allBtn) {
            allBtn.classList.toggle('is-active', selectedSlugs.length === 0);
        }

        root.classList.toggle('is-filtered', selectedSlugs.length > 0);
    }

    function refreshInjectedPosts(root) {
        document.dispatchEvent(
            new CustomEvent('academor:blog-posts-updated', { detail: { root: root } })
        );
        if (window.AcademorScroll && typeof window.AcademorScroll.initReveal === 'function') {
            window.AcademorScroll.initReveal();
        } else {
            root.querySelectorAll('.blog-card, .blog-featured-card').forEach(function (el) {
                el.classList.add('is-revealed', 'is-visible');
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
        }
    }

    function boot() {
        document.querySelectorAll('[data-blog-topic-filter]').forEach(function (root) {
            if (root.dataset.blogTopicReady) {
                return;
            }
            root.dataset.blogTopicReady = '1';

            var trigger = root.querySelector('[data-blog-topic-trigger]');
            var menu = root.querySelector('[data-blog-topic-menu]');
            var pageUrl = root.dataset.blogPageUrl || '/blog/';
            var apiUrl = root.dataset.blogApiUrl || pageUrl;
            var postsRoot = document.querySelector('[data-blog-posts-root]');
            var closeTimer = null;
            var animMs = 420;
            var fetchController = null;
            var activeRequestId = 0;

            if (!trigger || !menu || !postsRoot) {
                return;
            }

            function openMenu() {
                if (root.classList.contains('is-open')) {
                    return;
                }
                clearTimeout(closeTimer);
                menu.hidden = false;
                root.classList.add('is-open');
                trigger.setAttribute('aria-expanded', 'true');
                requestAnimationFrame(function () {
                    menu.classList.add('is-visible');
                });
            }

            function closeMenu() {
                if (!root.classList.contains('is-open')) {
                    return;
                }
                trigger.setAttribute('aria-expanded', 'false');
                menu.classList.remove('is-visible');
                root.classList.remove('is-open');
                clearTimeout(closeTimer);
                closeTimer = setTimeout(function () {
                    if (!root.classList.contains('is-open')) {
                        menu.hidden = true;
                    }
                }, animMs);
            }

            function setLoading(isLoading) {
                root.classList.toggle('is-loading', isLoading);
                postsRoot.classList.toggle('is-loading', isLoading);
                postsRoot.setAttribute('aria-busy', isLoading ? 'true' : 'false');
            }

            function applyFilter(selectedSlugs, pushState) {
                selectedSlugs = (selectedSlugs || []).slice().sort();
                var requestUrl = buildUrl(apiUrl, selectedSlugs);
                var requestId = ++activeRequestId;

                if (fetchController) {
                    fetchController.abort();
                }
                fetchController = new AbortController();
                setLoading(true);

                fetch(requestUrl, {
                    method: 'GET',
                    headers: {
                        Accept: 'text/html',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    signal: fetchController.signal,
                    credentials: 'same-origin',
                })
                    .then(function (response) {
                        if (!response.ok) {
                            throw new Error('Blog filter request failed: ' + response.status);
                        }
                        return response.text();
                    })
                    .then(function (html) {
                        if (requestId !== activeRequestId) {
                            return;
                        }
                        postsRoot.innerHTML = html;
                        syncCheckboxes(root, selectedSlugs);
                        updateFilterLabel(root, selectedSlugs);
                        refreshInjectedPosts(postsRoot);

                        if (pushState) {
                            history.pushState(
                                { blogTags: selectedSlugs },
                                '',
                                buildUrl(pageUrl, selectedSlugs)
                            );
                        }
                    })
                    .catch(function (err) {
                        if (err && err.name === 'AbortError') {
                            return;
                        }
                        window.location.href = buildUrl(pageUrl, selectedSlugs);
                    })
                    .finally(function () {
                        if (requestId === activeRequestId) {
                            setLoading(false);
                        }
                    });
            }

            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (root.classList.contains('is-open')) {
                    closeMenu();
                } else {
                    openMenu();
                }
            });

            document.addEventListener('click', function (e) {
                if (!root.contains(e.target)) {
                    closeMenu();
                }
            });

            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && root.classList.contains('is-open')) {
                    closeMenu();
                    trigger.focus();
                }
            });

            root.querySelectorAll('[data-blog-topic-option]').forEach(function (input) {
                input.addEventListener('change', function () {
                    applyFilter(getSelectedSlugs(root), true);
                });
            });

            var allBtn = root.querySelector('[data-blog-topic-all]');
            if (allBtn) {
                allBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    syncCheckboxes(root, []);
                    applyFilter([], true);
                });
            }

            window.addEventListener('popstate', function (e) {
                var slugs =
                    e.state && e.state.blogTags
                        ? e.state.blogTags.slice().sort()
                        : parseTagsFromSearch(window.location.search);
                syncCheckboxes(root, slugs);
                updateFilterLabel(root, slugs);
                applyFilter(slugs, false);
            });

            var initial = parseTagsFromSearch(window.location.search);
            history.replaceState(
                { blogTags: initial },
                '',
                window.location.pathname + window.location.search
            );

            var filterBar = document.querySelector('[data-blog-filter-bar]');
            var filterSentinel = document.querySelector('[data-blog-filter-sentinel]');
            if (filterBar && filterSentinel && 'IntersectionObserver' in window) {
                var stickyObserver = new IntersectionObserver(
                    function (entries) {
                        filterBar.classList.toggle('is-stuck', !entries[0].isIntersecting);
                    },
                    { root: null, threshold: 0, rootMargin: '-5.5rem 0px 0px 0px' }
                );
                stickyObserver.observe(filterSentinel);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
