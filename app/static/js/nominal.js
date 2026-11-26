// Peningkatan opsional: format ribuan saat mengetik. Tanpa file ini form tetap jalan (server menerima 15000 dan 15.000).
(function () {
    var input = document.getElementById("nominal");
    if (!input) return;
    function format() {
        var digits = input.value.replace(/\D/g, "").slice(0, 7);
        input.value = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }
    input.addEventListener("input", format);
    format();
})();
