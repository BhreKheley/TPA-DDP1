"""Modul Algoritma Anggaran & Knapsack DP (Budget Recommendation Engine)
Smart Meal Finder - DDP1 Gasal 2026/2027 Kelompok 5

Modul ini mengimplementasikan algoritma optimasi pemilihan kombinasi menu makanan
dan minuman berdasarkan batas anggaran (budget) mahasiswa Universitas Indonesia.

Penerapan Konsep Algoritma & Teori DDP1:
1. Pemrograman Dinamis (Dynamic Programming - 0/1 Knapsack):
   - Masalah: Dari sekumpulan menu makanan di kantin UI, pilih kombinasi menu
     sedemikian rupa sehingga total harga tidak melebihi anggaran pengguna,
     namun total kepuasan / gizi makanan (satisfaction score) bernilai maksimal.
   - Mengapa Knapsack 0/1? Setiap item hanya bisa dipilih maksimal 1 kali (0 = tidak dibeli, 1 = dibeli).
   - Matriks DP: dp[i][w] menyimpan nilai kepuasan maksimal dari subset i item pertama
     dengan batas kapasitas anggaran w.
2. Optimasi Skala FPB (Greatest Common Divisor / GCD Scaling):
   - Harga makanan di Indonesia adalah kelipatan ribuan/ratusan (cth: Rp 500, Rp 1.000).
   - Membagi seluruh harga dengan FPB memperkecil kolom matriks DP drastis,
     menghemat memori dan waktu komputasi O(N * W).
3. Penelusuran Balik (Backtracking):
   - Setelah tabel DP selesai dihitung, algoritma menelusuri kembali dari sel optimal
     untuk merekonstruksi daftar objek MenuItem yang terpilih.
4. Perhitungan Defisit (Deficit Analysis):
   - Jika uang mahasiswa lebih kecil dari harga menu termurah yang ada, sistem tidak
     menampilkan halaman kosong, melainkan menghitung menu termurah dan selisih
     kekurangan uangnya (Defisit = Harga Termurah - Uang Mahasiswa).

Kontributor:
- Bhre Nabil Faeyza (NPM: 2606887563) - Desain Algoritma Knapsack DP & Pengujian Pytest
- Johannes Praba Aji (NPM: 2606748465) - Reviewer PR #2 & Integrasi Web
"""

from dataclasses import dataclass
from functools import reduce
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.loader import (
    Category,
    MenuItem,
    Merchant,
    extract_all_items,
    filter_items,
)


class RecommendationError(Exception):
    """Base exception for budget and meal recommendation errors."""
    pass


@dataclass
class MealCombination:
    """Represents a recommended meal package fitting within a user's budget limit.

    Attributes:
        items: List of MenuItem objects comprising the meal.
        total_cost: Sum of menu item prices in IDR.
        budget_limit: User's specified budget ceiling.
        budget_remaining: Unspent budget balance (budget_limit - total_cost).
        total_satisfaction: Composite satisfaction score across items.
        is_exact_match: True if total_cost exactly equals budget_limit.
        canteen_names: Unique sorted list of canteens hosting the items.
        package_type: Categorical package tier ('optimal', 'hemat', 'combo').
    """
    items: List[MenuItem]
    total_cost: int
    budget_limit: int
    budget_remaining: int
    total_satisfaction: float
    is_exact_match: bool
    canteen_names: List[str]
    package_type: str  # 'optimal', 'hemat', 'combo'

    def to_dict(self) -> Dict[str, Any]:
        """Serializes combination to a dictionary for API and template rendering."""
        return {
            "items": [
                {
                    "id": it.id,
                    "name": it.name,
                    "category": it.category.value if hasattr(it.category, "value") else str(it.category),
                    "price": it.price,
                    "satisfaction_score": it.satisfaction_score,
                    "dietary_tags": sorted(list(it.dietary_tags)),
                    "merchant_id": it.merchant_id,
                    "merchant_name": it.merchant_name,
                    "canteen_name": it.canteen_name,
                    "faculty": it.faculty,
                    "calories": it.calories,
                    "description": it.description,
                    "is_available": it.is_available,
                }
                for it in self.items
            ],
            "total_cost": self.total_cost,
            "budget_limit": self.budget_limit,
            "budget_remaining": self.budget_remaining,
            "total_satisfaction": self.total_satisfaction,
            "is_exact_match": self.is_exact_match,
            "canteen_names": self.canteen_names,
            "package_type": self.package_type,
        }


@dataclass
class RecommendationResult:
    """Top-level container for budget recommendation results and deficit reporting.

    Attributes:
        status: Status code ('SUCCESS', 'INSUFFICIENT_BUDGET', 'NO_MATCHING_ITEMS').
        budget: Requested budget amount in IDR.
        recommendations: Ordered list of ranked MealCombination packages.
        cheapest_item_price: Minimum price required for a viable meal/combo.
        deficit: Shortfall amount in IDR when budget is insufficient.
        message: Human-friendly explanation message in Indonesian.
        fallback_recommendations: Alternative affordable options when strict combo exceeds budget.
    """
    status: str  # 'SUCCESS', 'INSUFFICIENT_BUDGET', 'NO_MATCHING_ITEMS'
    budget: int
    recommendations: List[MealCombination]
    cheapest_item_price: int
    deficit: int = 0
    message: str = ""
    fallback_recommendations: List[MealCombination] = None

    def __post_init__(self):
        if self.fallback_recommendations is None:
            self.fallback_recommendations = []

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result to a dictionary for JSON API responses."""
        res = {
            "status": self.status,
            "budget": self.budget,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "cheapest_item_price": self.cheapest_item_price,
            "deficit": self.deficit,
            "message": self.message,
        }
        if self.fallback_recommendations:
            res["fallback_recommendations"] = [rec.to_dict() for rec in self.fallback_recommendations]
        return res


def knapsack_01_dp(items: List[MenuItem], budget: int) -> Tuple[List[MenuItem], int, float]:
    """Pure 0/1 knapsack dynamic programming maximizing satisfaction score within budget.

    Includes greatest common divisor (GCD) capacity scaling and mass budget
    short-circuit optimization for O(N) handling of large budgets.

    Args:
        items: List of MenuItem candidates available for selection.
        budget: Maximum budget constraint in IDR.

    Returns:
        Tuple of (selected_items, total_cost, total_satisfaction).
    """
    if budget <= 0 or not items:
        return ([], 0, 0.0)

    # Filter items that are individually affordable and have non-negative satisfaction
    eligible = [it for it in items if 0 <= it.price <= budget and it.satisfaction_score >= 0]
    if not eligible:
        return ([], 0, 0.0)

    total_eligible_price = sum(it.price for it in eligible)
    # Mass budget short-circuit: if all items fit within budget, return all in O(N)
    if budget >= total_eligible_price:
        total_sat = round(sum(it.satisfaction_score for it in eligible), 4)
        return (list(eligible), total_eligible_price, total_sat)

    # Compute GCD of positive prices to scale table capacity dimension
    positive_prices = [it.price for it in eligible if it.price > 0]
    gcd_scale = reduce(math.gcd, positive_prices) if positive_prices else 1
    if gcd_scale < 1:
        gcd_scale = 1

    scaled_weights = [it.price // gcd_scale for it in eligible]
    scaled_capacity = min(budget, total_eligible_price) // gcd_scale

    n = len(eligible)
    # Construct 2D DP table: dp[i][w] stores maximum satisfaction using subset of first i items
    dp = [[0.0] * (scaled_capacity + 1) for _ in range(n + 1)]
    # min_cost[i][w] stores the minimum cost in IDR achieving dp[i][w]
    min_cost = [[0] * (scaled_capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = scaled_weights[i - 1]
        val = eligible[i - 1].satisfaction_score
        price = eligible[i - 1].price
        for w in range(scaled_capacity + 1):
            if w < wt:
                dp[i][w] = dp[i - 1][w]
                min_cost[i][w] = min_cost[i - 1][w]
            else:
                exclude_val = dp[i - 1][w]
                exclude_cost = min_cost[i - 1][w]
                include_val = dp[i - 1][w - wt] + val
                include_cost = min_cost[i - 1][w - wt] + price

                if include_val > exclude_val + 1e-9:
                    dp[i][w] = include_val
                    min_cost[i][w] = include_cost
                elif abs(include_val - exclude_val) <= 1e-9 and include_cost < exclude_cost:
                    # Secondary criteria: prefer lower cost for equal satisfaction
                    dp[i][w] = include_val
                    min_cost[i][w] = include_cost
                else:
                    dp[i][w] = exclude_val
                    min_cost[i][w] = exclude_cost

    # Determine tightest capacity achieving the global optimal satisfaction
    best_w = scaled_capacity
    best_val = dp[n][scaled_capacity]
    for w in range(scaled_capacity + 1):
        if abs(dp[n][w] - best_val) < 1e-9 and min_cost[n][w] == min_cost[n][scaled_capacity]:
            best_w = w
            break

    # Backtracking to reconstruct selected items
    selected: List[MenuItem] = []
    curr_w = best_w
    for i in range(n, 0, -1):
        wt = scaled_weights[i - 1]
        val = eligible[i - 1].satisfaction_score
        price = eligible[i - 1].price
        if curr_w >= wt:
            inc_val = dp[i - 1][curr_w - wt] + val
            inc_cost = min_cost[i - 1][curr_w - wt] + price
            if (
                abs(dp[i][curr_w] - inc_val) < 1e-9
                and min_cost[i][curr_w] == inc_cost
                and (dp[i][curr_w] > dp[i - 1][curr_w] + 1e-9 or min_cost[i][curr_w] < min_cost[i - 1][curr_w])
            ):
                selected.append(eligible[i - 1])
                curr_w -= wt

    selected.reverse()
    total_cost = sum(it.price for it in selected)
    total_sat = round(sum(it.satisfaction_score for it in selected), 4)
    return (selected, total_cost, total_sat)


def _is_food(item: MenuItem) -> bool:
    """Helper to check if a MenuItem belongs to the Food category."""
    cat = item.category
    return cat == Category.FOOD or str(cat).lower() == "food"


def _is_beverage(item: MenuItem) -> bool:
    """Helper to check if a MenuItem belongs to the Beverage category."""
    cat = item.category
    return cat == Category.BEVERAGE or str(cat).lower() == "beverage"


def _is_snack(item: MenuItem) -> bool:
    """Helper to check if a MenuItem belongs to the Snack category."""
    cat = item.category
    return cat == Category.SNACK or str(cat).lower() == "snack"


def recommend_meals(
    merchants_or_items: Union[List[Merchant], List[MenuItem]],
    budget: int,
    canteen_filter: Optional[str] = None,
    dietary_preferences: Optional[List[str]] = None,
    require_combo: bool = True,
    top_k: int = 5,
    food_only: bool = False,
) -> RecommendationResult:
    """Category-constrained meal recommendation optimizer.

    Generates realistic student meal packages (1 Food + 1 Drink combos, deluxe
    packages, or solo fallback), strictly partitioned per canteen. Calculates
    deficits when budget is insufficient, flags exact matches, and provides
    multi-criteria top-K ranking.

    Args:
        merchants_or_items: Input list of Merchant objects or flat MenuItem objects.
        budget: User's available budget in IDR.
        canteen_filter: Optional canteen name substring filter (case-insensitive).
        dietary_preferences: Optional list of dietary tag requirements (e.g. ['halal']).
        require_combo: If True, enforces 1 Food + 1 Beverage balanced meal packages.
        top_k: Maximum number of ranked recommendations to return.
        food_only: If True, restricts candidates to Food category only (Bawa Tumbler mode).

    Returns:
        RecommendationResult with status, recommendations list, deficit, and messages.
    """
    # 1. Normalize input item collection
    if not merchants_or_items:
        return RecommendationResult(
            status="NO_MATCHING_ITEMS",
            budget=budget,
            recommendations=[],
            cheapest_item_price=0,
            deficit=0,
            message="Tidak ada data merchant atau menu yang tersedia.",
        )

    if isinstance(merchants_or_items[0], Merchant):
        all_items = extract_all_items(merchants_or_items, only_available=True)
    else:
        all_items = [it for it in merchants_or_items if getattr(it, "is_available", True)]

    # 2. Filter items by canteen and dietary tags
    clean_canteen = canteen_filter.strip() if canteen_filter and canteen_filter.strip() else None
    clean_tags = (
        {str(t).strip().lower() for t in dietary_preferences if str(t).strip()}
        if dietary_preferences
        else None
    )
    if clean_tags and len(clean_tags) == 0:
        clean_tags = None

    filtered_items = filter_items(
        all_items,
        canteen_name=clean_canteen,
        required_tags=clean_tags,
    )

    if not filtered_items:
        return RecommendationResult(
            status="NO_MATCHING_ITEMS",
            budget=budget,
            recommendations=[],
            cheapest_item_price=0,
            deficit=0,
            message="Tidak ada menu yang sesuai dengan filter yang dipilih.",
        )

    # 2b. Bawa Tumbler mode: restrict candidates to Food items only
    if food_only:
        filtered_items = [it for it in filtered_items if _is_food(it)]
        if not filtered_items:
            return RecommendationResult(
                status="NO_MATCHING_ITEMS",
                budget=budget,
                recommendations=[],
                cheapest_item_price=0,
                deficit=0,
                message="Tidak ada menu makanan yang sesuai filter (mode Bawa Tumbler).",
            )

    # 3. Partition items by canteen (combos must be co-located within the same canteen)
    canteen_groups: Dict[str, List[MenuItem]] = {}
    for it in filtered_items:
        canteen_groups.setdefault(it.canteen_name, []).append(it)

    pool_has_foods = any(_is_food(it) for it in filtered_items)
    pool_has_bevs = any(_is_beverage(it) for it in filtered_items)

    # 4. Generate candidate meal combinations per canteen
    raw_candidates: List[Tuple[MenuItem, ...]] = []

    for _, c_items in canteen_groups.items():
        foods = [it for it in c_items if _is_food(it)]
        bevs = [it for it in c_items if _is_beverage(it)]
        snacks = [it for it in c_items if _is_snack(it)]

        if require_combo:
            if foods and bevs:
                # Standard combo: 1 Food + 1 Beverage
                for f in foods:
                    for b in bevs:
                        raw_candidates.append((f, b))
                # Deluxe combo: 1 Food + 1 Beverage + 1 Snack
                for f in foods:
                    for b in bevs:
                        for s in snacks:
                            raw_candidates.append((f, b, s))
            elif foods and not pool_has_bevs:
                # Graceful fallback: solo food when no beverages exist in the entire filtered pool
                for f in foods:
                    raw_candidates.append((f,))
            elif bevs and not pool_has_foods:
                # Graceful fallback: solo drink when no foods exist in the entire filtered pool
                for b in bevs:
                    raw_candidates.append((b,))
            elif not pool_has_foods and not pool_has_bevs:
                for s in snacks:
                    raw_candidates.append((s,))
        else:
            # Flexible combinations (require_combo=False)
            if foods and bevs:
                for f in foods:
                    for b in bevs:
                        raw_candidates.append((f, b))
            if snacks and bevs:
                # Quick study break: 1 Snack + 1 Beverage
                for s in snacks:
                    for b in bevs:
                        raw_candidates.append((s, b))
            if foods and bevs and snacks:
                for f in foods:
                    for b in bevs:
                        for s in snacks:
                            raw_candidates.append((f, b, s))
            # Solo items
            for it in c_items:
                raw_candidates.append((it,))

    # Deduplicate candidate tuples using sorted item ID signatures
    unique_candidates: List[Tuple[MenuItem, ...]] = []
    seen_combos: Set[Tuple[str, ...]] = set()
    for cand in raw_candidates:
        sig = tuple(sorted(it.id for it in cand))
        if sig not in seen_combos:
            seen_combos.add(sig)
            unique_candidates.append(cand)

    if not unique_candidates:
        return RecommendationResult(
            status="NO_MATCHING_ITEMS",
            budget=budget,
            recommendations=[],
            cheapest_item_price=0,
            deficit=0,
            message="Tidak dapat membentuk kombinasi menu yang valid.",
        )

    # 5. Determine cheapest viable combination and evaluate budget deficit
    cheapest_combo_price = min(sum(it.price for it in cand) for cand in unique_candidates)

    if budget < cheapest_combo_price:
        deficit = cheapest_combo_price - budget
        fallback_recs: List[MealCombination] = []
        if require_combo and budget > 0:
            try:
                alt_res = recommend_meals(
                    merchants_or_items=filtered_items,
                    budget=budget,
                    canteen_filter=clean_canteen,
                    dietary_preferences=list(clean_tags) if clean_tags else None,
                    require_combo=False,
                    top_k=top_k,
                    food_only=food_only,
                )
                if alt_res.status == "SUCCESS":
                    fallback_recs = alt_res.recommendations
            except Exception:
                fallback_recs = []

        return RecommendationResult(
            status="INSUFFICIENT_BUDGET",
            budget=budget,
            recommendations=[],
            cheapest_item_price=cheapest_combo_price,
            deficit=deficit,
            message=f"Budget Rp {budget:,} kurang Rp {deficit:,} untuk paket termurah (Rp {cheapest_combo_price:,}).",
            fallback_recommendations=fallback_recs,
        )

    # 6. Filter affordable candidates and instantiate MealCombination objects
    affordable_combos: List[MealCombination] = []
    for cand in unique_candidates:
        cost = sum(it.price for it in cand)
        if cost <= budget:
            items_list = list(cand)
            sat = round(sum(it.satisfaction_score for it in items_list), 2)
            c_names = sorted(list({it.canteen_name for it in items_list}))
            combo_obj = MealCombination(
                items=items_list,
                total_cost=cost,
                budget_limit=budget,
                budget_remaining=budget - cost,
                total_satisfaction=sat,
                is_exact_match=(cost == budget),
                canteen_names=c_names,
                package_type="combo",
            )
            affordable_combos.append(combo_obj)

    # 7. Multi-criteria ranking:
    # Primary: satisfaction descending, Secondary: cost ascending, Tertiary: deterministic item IDs
    affordable_combos.sort(
        key=lambda c: (-c.total_satisfaction, c.total_cost, tuple(sorted(it.id for it in c.items)))
    )

    # Guarantee exact match combinations are present in the final pool if any exist
    exact_matches = [c for c in affordable_combos if c.is_exact_match]
    selected_pool: List[MealCombination] = list(affordable_combos[:top_k])
    selected_sigs: Set[Tuple[str, ...]] = {
        tuple(sorted(it.id for it in c.items)) for c in selected_pool
    }

    if exact_matches:
        for em in exact_matches:
            em_sig = tuple(sorted(it.id for it in em.items))
            if em_sig not in selected_sigs:
                if len(selected_pool) >= top_k:
                    # Replace the lowest satisfaction candidate in the pool
                    selected_pool[-1] = em
                else:
                    selected_pool.append(em)
                selected_sigs.add(em_sig)
                break

    # Re-sort final pool to strictly maintain non-increasing satisfaction order
    selected_pool.sort(
        key=lambda c: (-c.total_satisfaction, c.total_cost, tuple(sorted(it.id for it in c.items)))
    )
    final_recs = selected_pool[:top_k]

    # 8. Assign package classifications ('optimal', 'hemat', 'combo')
    if final_recs:
        final_recs[0].package_type = "optimal"
        if len(final_recs) > 1:
            # Assign 'hemat' to the candidate with minimum cost
            min_cost_idx = min(range(len(final_recs)), key=lambda idx: final_recs[idx].total_cost)
            if min_cost_idx != 0:
                final_recs[min_cost_idx].package_type = "hemat"
            else:
                # If rank 0 also has the minimum cost, rank 1 gets 'hemat'
                final_recs[1].package_type = "hemat"

            for idx in range(len(final_recs)):
                if idx != 0 and final_recs[idx].package_type not in ("optimal", "hemat"):
                    final_recs[idx].package_type = "combo"
        else:
            final_recs[0].package_type = "hemat" if final_recs[0].total_cost <= budget * 0.75 else "optimal"

    return RecommendationResult(
        status="SUCCESS",
        budget=budget,
        recommendations=final_recs,
        cheapest_item_price=cheapest_combo_price,
        deficit=0,
        message=f"Berhasil menemukan {len(final_recs)} rekomendasi menu.",
    )
