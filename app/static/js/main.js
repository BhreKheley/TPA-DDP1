/**
 * Smart Meal Finder — interactivity
 * DDP1 Kelompok 5 (Johannes Praba Aji - 2606748465)
 */

document.addEventListener('DOMContentLoaded', function () {
    // ── 1. Mobile nav toggle ──────────────────────────────────────────────
    var navToggle = document.getElementById('nav-toggle');
    var navMenu   = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            var isOpen = navMenu.classList.toggle('open');
            navToggle.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        document.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                navMenu.classList.remove('open');
                navToggle.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // ── 2. Currency formatter ─────────────────────────────────────────────
    function fmt(amount) {
        if (!amount || isNaN(amount)) return 'Rp 0';
        return 'Rp ' + parseInt(amount, 10).toLocaleString('id-ID');
    }

    // ── 3. Budget input ───────────────────────────────────────────────────
    var budgetInput  = document.getElementById('budget-input');
    var budgetPreview = document.getElementById('budget-preview');
    var presetChips  = document.querySelectorAll('.preset-chip');

    if (budgetInput && budgetPreview) {
        budgetInput.addEventListener('input', function () {
            var val = budgetInput.value.trim();
            budgetPreview.textContent = fmt(val);

            presetChips.forEach(function (chip) {
                chip.classList.toggle('active', chip.getAttribute('data-amount') === val);
            });
        });

        if (budgetInput.value) {
            budgetPreview.textContent = fmt(budgetInput.value);
        }
    }

    // ── 4. Preset chip handlers ──────────────────────────────────────────
    var flexRadio   = document.getElementById('combo-flexible');
    var strictRadio = document.getElementById('combo-strict');
    var tumblerRadio = document.getElementById('combo-tumbler');
    var foodOnlyHidden = document.getElementById('food-only-hidden');

    function setComboMode(combo, foodOnly) {
        if (!flexRadio) return;
        if (foodOnly === 'on') {
            if (tumblerRadio) tumblerRadio.checked = true;
            if (foodOnlyHidden) foodOnlyHidden.value = 'on';
        } else if (combo === 'off') {
            flexRadio.checked = true;
            if (foodOnlyHidden) foodOnlyHidden.value = 'off';
        } else {
            if (strictRadio) strictRadio.checked = true;
            if (foodOnlyHidden) foodOnlyHidden.value = 'off';
        }
    }

    presetChips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            var amount   = chip.getAttribute('data-amount');
            var combo    = chip.getAttribute('data-combo');
            var foodOnly = chip.getAttribute('data-food-only') || 'off';

            if (budgetInput && amount) {
                budgetInput.value = amount;
                if (budgetPreview) budgetPreview.textContent = fmt(amount);

                presetChips.forEach(function (c) { c.classList.remove('active'); });
                chip.classList.add('active');

                setComboMode(combo, foodOnly);
                budgetInput.focus();
            }
        });
    });

    // ── 5. Tumbler radio → hidden field sync ──────────────────────────────
    // When user manually picks a radio, keep the hidden food_only field in sync
    [flexRadio, strictRadio, tumblerRadio].forEach(function (radio) {
        if (!radio) return;
        radio.addEventListener('change', function () {
            if (!foodOnlyHidden) return;
            foodOnlyHidden.value = (radio.id === 'combo-tumbler') ? 'on' : 'off';
        });
    });

    // ── 6. Submit feedback ────────────────────────────────────────────────
    var searchForm = document.getElementById('recommend-form');
    var submitBtn  = document.getElementById('submit-search-btn');
    if (searchForm && submitBtn) {
        searchForm.addEventListener('submit', function () {
            submitBtn.style.opacity = '0.85';
            submitBtn.innerHTML = '<span>Lagi dihitung...</span>';
        });
    }
});
