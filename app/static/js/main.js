/**
 * Smart Meal Finder - Interactive Client-side Script
 * DDP1 Kelompok 5 (Johannes Praba Aji - 2606748465)
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Navigation Toggle & Auto-Close
    var navToggle = document.getElementById('nav-toggle');
    var navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            var isOpen = navMenu.classList.toggle('open');
            navToggle.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        // Close menu when clicking outside or clicking any nav link
        document.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                navMenu.classList.remove('open');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // 2. Format Currency Helper
    function formatRupiahDisplay(amount) {
        if (!amount || isNaN(amount)) return 'Rp 0';
        var num = parseInt(amount, 10);
        return 'Rp ' + num.toLocaleString('id-ID');
    }

    // 3. Live Budget Input Preview & Preset Buttons
    var budgetInput = document.getElementById('budget-input');
    var budgetPreview = document.getElementById('budget-preview');
    var presetChips = document.querySelectorAll('.preset-chip');

    if (budgetInput && budgetPreview) {
        // Update on typing
        budgetInput.addEventListener('input', function () {
            var val = budgetInput.value.trim();
            budgetPreview.textContent = formatRupiahDisplay(val);

            // Update active preset styling
            presetChips.forEach(function (chip) {
                if (chip.getAttribute('data-amount') === val) {
                    chip.classList.add('active');
                } else {
                    chip.classList.remove('active');
                }
            });
        });

        // Initialize preview if input has default value
        if (budgetInput.value) {
            budgetPreview.textContent = formatRupiahDisplay(budgetInput.value);
        }
    }

    // Preset Chip Click Handlers
    presetChips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            var amount = chip.getAttribute('data-amount');
            var combo = chip.getAttribute('data-combo');
            if (budgetInput && amount) {
                budgetInput.value = amount;
                if (budgetPreview) {
                    budgetPreview.textContent = formatRupiahDisplay(amount);
                }

                presetChips.forEach(function (c) { c.classList.remove('active'); });
                chip.classList.add('active');

                // Auto-adjust format toggle if specified (e.g. 10k suggests flexible mode)
                if (combo === 'off') {
                    var flexibleRadio = document.getElementById('combo-flexible');
                    if (flexibleRadio) flexibleRadio.checked = true;
                } else if (combo === 'on') {
                    var strictRadio = document.getElementById('combo-strict');
                    if (strictRadio) strictRadio.checked = true;
                }

                budgetInput.focus();
            }
        });
    });

    // 4. Form Submit Instant Feedback
    var searchForm = document.getElementById('recommend-form');
    var submitBtn = document.getElementById('submit-search-btn');
    if (searchForm && submitBtn) {
        searchForm.addEventListener('submit', function () {
            submitBtn.style.opacity = '0.85';
            submitBtn.innerHTML = '<span>Menghitung Rekomendasi Menu...</span>';
        });
    }
});
