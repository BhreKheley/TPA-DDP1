/**
 * Smart Meal Finder - Client-Side Interactions
 * DDP1 Kelompok 5 (Johannes Praba Aji - 2606748465)
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Navigation Drawer + Escape Key Handling (R-32)
    var navToggle = document.getElementById('nav-toggle');
    var navMenu = document.getElementById('nav-menu');

    function closeMobileNav() {
        if (navMenu && navToggle) {
            navMenu.classList.remove('open');
            navToggle.classList.remove('active');
            navToggle.setAttribute('aria-expanded', 'false');
        }
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            var isOpen = navMenu.classList.toggle('open');
            navToggle.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        navMenu.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', closeMobileNav);
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && navMenu.classList.contains('open')) {
                closeMobileNav();
                navToggle.focus();
            }
        });
    }

    // 2. Rupiah Formatter
    function formatRupiahDisplay(amount) {
        if (amount === '' || amount === null || isNaN(amount)) return 'Rp 0';
        var num = parseInt(amount, 10);
        if (num < 0) return 'Rp 0';
        return 'Rp ' + num.toLocaleString('id-ID');
    }

    // 3. Home Planner: Budget Input Preview & Mode-Synced Presets
    var budgetInput = document.getElementById('budget-input');
    var budgetPreview = document.getElementById('budget-preview');
    var presetChips = document.querySelectorAll('.preset-chip');

    function syncPresetHighlight(rawValue) {
        presetChips.forEach(function (chip) {
            if (chip.getAttribute('data-amount') === rawValue) {
                chip.classList.add('active');
            } else {
                chip.classList.remove('active');
            }
        });
    }

    if (budgetInput && budgetPreview) {
        budgetInput.addEventListener('input', function () {
            var val = budgetInput.value.trim();
            budgetPreview.textContent = formatRupiahDisplay(val);
            syncPresetHighlight(val);
        });

        if (budgetInput.value) {
            budgetPreview.textContent = formatRupiahDisplay(budgetInput.value.trim());
        }
    }

    presetChips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            var amount = chip.getAttribute('data-amount');
            var suggestedMode = chip.getAttribute('data-mode');
            if (budgetInput && amount) {
                budgetInput.value = amount;
                if (budgetPreview) {
                    budgetPreview.textContent = formatRupiahDisplay(amount);
                }
                syncPresetHighlight(amount);

                if (suggestedMode) {
                    var targetRadio = document.getElementById('mode-' + suggestedMode);
                    if (targetRadio) targetRadio.checked = true;
                }
                budgetInput.focus();
            }
        });
    });

    // 4. Form Submit Loading Indicator
    var searchForm = document.getElementById('recommend-form');
    var submitBtn = document.getElementById('submit-search-btn');
    if (searchForm && submitBtn) {
        searchForm.addEventListener('submit', function () {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Menghitung Paket Menu...';
        });
    }

    // 5. Merchants Catalog: Live Search & Category Filter
    var searchInput = document.getElementById('menu-search-input');
    var categoryPills = document.querySelectorAll('.cat-pill');
    var merchantCards = document.querySelectorAll('.merchant-card');
    var emptyStateCard = document.getElementById('catalog-empty-state');
    var resetBtn = document.getElementById('reset-catalog-filter');
    var activeCategory = 'all';

    function applyCatalogFilter() {
        if (!merchantCards.length) return;
        var query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        var visibleMerchants = 0;

        merchantCards.forEach(function (card) {
            var merchantText = card.getAttribute('data-merchant-text') || '';
            var merchantMatchesQuery = query === '' || merchantText.indexOf(query) !== -1;
            var rows = card.querySelectorAll('.menu-row');
            var visibleRows = 0;

            rows.forEach(function (row) {
                var itemCat = row.getAttribute('data-item-category') || '';
                var itemName = row.getAttribute('data-item-name') || '';

                var catMatch = activeCategory === 'all' || itemCat === activeCategory;
                var textMatch = query === '' || merchantMatchesQuery || itemName.indexOf(query) !== -1;

                if (catMatch && textMatch) {
                    row.classList.remove('hidden');
                    visibleRows++;
                } else {
                    row.classList.add('hidden');
                }
            });

            if (visibleRows > 0) {
                card.classList.remove('hidden');
                visibleMerchants++;
            } else {
                card.classList.add('hidden');
            }
        });

        if (emptyStateCard) {
            if (visibleMerchants === 0) {
                emptyStateCard.classList.remove('hidden');
            } else {
                emptyStateCard.classList.add('hidden');
            }
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyCatalogFilter);
    }

    categoryPills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            activeCategory = pill.getAttribute('data-category') || 'all';
            categoryPills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            applyCatalogFilter();
        });
    });

    if (resetBtn) {
        resetBtn.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            activeCategory = 'all';
            categoryPills.forEach(function (p) {
                p.classList.toggle('active', p.getAttribute('data-category') === 'all');
            });
            applyCatalogFilter();
        });
    }
});
