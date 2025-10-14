import numpy as np
import torch
from .utils import compute_recipe_metrics, analyze_tie_tolerance_impact
from numba import njit, prange


@njit(parallel=True)
def numba_calculate_utility_gain(
    U_np, selected_wines_arr, top_k, weights_arr, num_recipes, num_wines, current_utility_per_recipe
):
    """
    Calculates the utility gain for every candidate wine j by simulating
    its addition to the top-K set for all recipes.

    Parameters:
    U_np : np.ndarray [num_recipes x num_wines]
        Utility matrix.
    selected_wines_arr : np.ndarray [num_selected]
        Indices of already selected wines (must be an array for Numba).
    top_k : int
        Only top-K wines per recipe contribute.
    weights_arr : np.ndarray [top_k]
        Weight for each position in top-K.
    num_recipes : int
    num_wines : int
    current_utility_per_recipe : np.ndarray [num_recipes]
        Pre-calculated utility of the current selected set for each recipe.

    Returns:
    utility_gains : np.ndarray [num_wines]
        Calculated utility gain for each wine j.
    """
    utility_gains = np.zeros(num_wines, dtype=np.float64)
    num_selected = len(selected_wines_arr)

    for j in prange(num_wines):
        # Do not calculate gain for already selected wines
        is_selected = False
        for s_idx in range(num_selected):
            if selected_wines_arr[s_idx] == j:
                is_selected = True
                break
        if is_selected:
            utility_gains[j] = -np.inf
            continue

        total_gain = 0.0

        for i in range(num_recipes):
            wine_utility = U_np[i, j]

            # Wine j must have positive utility to contribute
            if wine_utility <= 0.0:
                continue

            # Step 1: Combine current selected and candidate j utilities
            # Numba needs fixed-size arrays, so we can't easily handle
            # the list of tuples. Instead, we work with the utilities array.

            # Temporary array for utilities: selected + candidate j
            # Max size is num_selected + 1. If it's larger than top_k,
            # we only care about the top_k+1 utilities.

            # Since we can't easily pass the recipe_top_wines structure (list of lists of tuples),
            # we reconstruct the set of utilities relevant to recipe i from the U matrix
            # and the *selected_wines_arr*. This is a compromise for Numba compatibility.

            # Array to hold utilities for current selected wines (and candidate j)
            # Max size: top_k + 1 (if the current set is already full)

            # Optimized utility set: current top-k utilities + wine_utility
            # A more Numba-friendly way to maintain the state is to keep
            # the *full* utility vector for all selected wines *per recipe*.
            # This is still memory-intensive.

            # Reverting to the most practical Numba approach:
            # Reconstruct current *selected* utilities for recipe i + candidate j utility

            # The current state only matters for the top-k wines already selected.
            # We'll use a local array to store the utilities of the current top wines
            # and the candidate wine j.

            # Collect utilities for currently selected wines
            current_utilities_i = np.empty(num_selected, dtype=np.float64)
            valid_count = 0
            for s_idx in range(num_selected):
                u_s = U_np[i, selected_wines_arr[s_idx]]
                if u_s > 0:
                    current_utilities_i[valid_count] = u_s
                    valid_count += 1

            # Create the combined utility array (current valid + candidate j)
            combined_utilities = np.empty(valid_count + 1, dtype=np.float64)
            combined_utilities[:valid_count] = current_utilities_i[:valid_count]
            combined_utilities[valid_count] = wine_utility

            # Sort the combined utilities to find the new top-K
            # Use insertion sort for small arrays (k+1) - Numba is good at this

            # Sort descending
            combined_utilities = -np.sort(-combined_utilities)

            # Step 2: Calculate the new weighted utility
            new_utility = 0.0
            num_to_sum = min(len(combined_utilities), top_k)
            for k in range(num_to_sum):
                new_utility += weights_arr[k] * combined_utilities[k]

            # Step 3: Calculate gain
            gain = new_utility - current_utility_per_recipe[i]
            total_gain += gain

        utility_gains[j] = total_gain

    return utility_gains


def greedy_select_topk_weighted(
    U,
    C,
    caps,
    W_E,
    max_card_size=999,
    verbose=False,
    top_k=3,
    weights=None,
    lambda_div=0.3,
    tie_tolerance=0.02,
    tie_method="adaptive",
):
    # Ensure U is NumPy
    if torch.is_tensor(U):
        U_np = U.cpu().numpy().astype(float)
    else:
        U_np = U.astype(float)

    num_recipes, num_wines = U_np.shape
    num_constraints = C.shape[1]

    # Default weights: exponential decay
    if weights is None:
        weights = np.array([0.6**i for i in range(top_k)], dtype=np.float64)
        weights[0] = 1.0  # Best wine gets full weight
    else:
        weights = np.array(weights, dtype=np.float64)

    current_counts = np.zeros(num_constraints, dtype=int)
    selected = []

    # We will now maintain the *current weighted utility* per recipe
    # instead of the complex top-K structure. This is required for Numba's
    # optimized utility gain calculation.
    current_utility_per_recipe = np.zeros(num_recipes, dtype=np.float64)

    # Track selected wines per constraint group for diversity
    selected_per_group = {k: [] for k in range(num_constraints)}

    # Normalize wine embeddings for cosine similarity
    if torch.is_tensor(W_E):
        W_E_norm = W_E / W_E.norm(dim=1, keepdim=True)
        W_E_np = W_E_norm.detach().cpu().numpy()
    else:
        W_E_norm = W_E / np.linalg.norm(W_E, axis=1, keepdims=True)
        W_E_np = W_E_norm

    # Pre-filter wines that have 0 utility for all recipes (optional but good)
    # valid_wine_mask = np.any(U_np > 0, axis=0)

    # While we have not reached max cardinality or exhausted all constraint capacity
    while len(selected) < max_card_size and len(selected) < sum(caps):        
        # Use an array for selected wines for Numba
        selected_arr = np.array(selected, dtype=np.int32)

        # --- Numba Optimized Utility Gain Calculation ---
        utility_gains = numba_calculate_utility_gain(
            U_np, selected_arr, top_k, weights, num_recipes, num_wines, current_utility_per_recipe
        )
        # ---------------------------------------------

        scores = np.full(num_wines, -np.inf)
        diversity_gains = np.zeros(num_wines)

        for j in range(num_wines):
            if j in selected:
                continue

            # Check constraints
            if np.any(current_counts + C[j] > caps):
                scores[j] = -np.inf
                continue

            groups_j = np.where(C[j] == 1)[0]
            if len(groups_j) == 0:
                scores[j] = -np.inf
                continue

            # Only compute diversity gain for feasible, non-selected wines

            # Compute diversity gain
            div_gain = 0.0
            for k in groups_j:
                selected_indices = selected_per_group[k]
                if len(selected_indices) == 0:
                    div_gain += 1.0
                else:
                    # Using np.dot for cosine similarity (W_E_np is normalized)
                    # NOTE: W_E_np[j:j+1] is needed to maintain the 2D shape for dot product
                    sims = np.dot(W_E_np[j : j + 1], W_E_np[selected_indices].T)
                    avg_sim = sims.mean()
                    div_gain += 1 - avg_sim
            div_gain /= len(groups_j)
            diversity_gains[j] = div_gain

        # Normalize components
        utility_max = utility_gains[np.isfinite(utility_gains)].max()
        diversity_max = diversity_gains.max()

        if utility_max > 0:
            utility_norm = utility_gains / utility_max
        else:
            utility_norm = utility_gains

        if diversity_max > 0:
            diversity_norm = diversity_gains / diversity_max
        else:
            diversity_norm = diversity_gains

        # Compute combined score
        # Note: utility_norm already contains -inf for selected/infeasible
        scores = (1 - lambda_div) * utility_norm + lambda_div * diversity_norm

        best_score = np.nanmax(scores)
        # if not np.isfinite(best_score) or best_score <= 0:
        #     if verbose:
        #         print("No feasible or beneficial wines remaining.")
        #     break

        # Determine tie candidates based on method
        if tie_method == "adaptive":
            threshold = best_score * (1 - tie_tolerance)
            best_candidates = np.where(scores >= threshold)[0]
        elif tie_method == "absolute":
            threshold = best_score - tie_tolerance
            best_candidates = np.where(scores >= threshold)[0]
        elif tie_method == "top_n":
            n = max(1, int(tie_tolerance))
            n = min(n, np.sum(np.isfinite(scores) & (scores > 0)))

            # Use argpartition on only the valid positive scores
            valid_indices = np.where(np.isfinite(scores) & (scores > 0))[0]
            if len(valid_indices) == 0:
                break

            temp_scores = scores[valid_indices]
            top_indices_local = np.argpartition(temp_scores, -n)[-n:]
            best_candidates = valid_indices[top_indices_local]
        else:
            raise ValueError(f"Unknown tie_method: {tie_method}")

        # Filter out candidates that are more than 10% worse than best
        # (This is a safety check from the original logic, not a core tie-breaker)
        quality_threshold = best_score * 0.90
        best_candidates = best_candidates[scores[best_candidates] >= quality_threshold]

        if len(best_candidates) == 0:
            best_candidates = np.array([np.argmax(scores)])

        best_wine = np.random.choice(best_candidates)
        selected.append(best_wine)

        # Update current_utility_per_recipe (The most critical part!)
        # Recalculate the *new* current utility for all recipes with the new selected set.

        # Utilities of all currently selected wines
        U_selected = U_np[:, selected]

        # Pre-allocate array for top_k utilities for sorting
        temp_utilities = np.zeros(top_k, dtype=np.float64)

        new_total_utility = 0.0
        for i in range(num_recipes):
            utilities = U_selected[i, :]  # Utilities for recipe i from selected set

            if len(utilities) > 0:
                # Find the top-K utilities
                if len(utilities) >= top_k:
                    # Argpartition is faster than full sort
                    top_indices = np.argpartition(utilities, -top_k)[-top_k:]
                    top_k_utils = utilities[top_indices]
                    top_k_utils.sort()  # Sort the top-K descending
                    top_k_utils = top_k_utils[::-1]
                else:
                    top_k_utils = np.sort(utilities)[::-1]

                # Calculate new weighted utility
                new_util_i = 0.0
                num_to_sum = len(top_k_utils)
                for k in range(num_to_sum):
                    new_util_i += weights[k] * top_k_utils[k]
            else:
                new_util_i = 0.0

            current_utility_per_recipe[i] = new_util_i
            new_total_utility += new_util_i

        # Update constraint counts and diversity tracking
        groups_best = np.where(C[best_wine] == 1)[0]
        for k in groups_best:
            selected_per_group[k].append(best_wine)
        current_counts += C[best_wine]

        if verbose:
            # Calculate current coverage (top-K slots with max bin) for logging
            current_coverage = 0
            max_bin = U_np.max()
            for i in range(num_recipes):
                utilities = U_selected[i, :]
                if len(utilities) > 0:
                    top_k_utils_temp = np.sort(utilities)[::-1][:top_k]
                    current_coverage += sum(1 for u in top_k_utils_temp if u == max_bin)

            max_possible = num_recipes * top_k

            # Analyze tie pool quality
            tie_analysis = analyze_tie_tolerance_impact(scores, tie_tolerance, tie_method)

            print(
                f"Step {len(selected):2d} | Added wine {best_wine:3d} | "
                f"Utility gain = {utility_gains[best_wine]:8.3f} | "
                f"Diversity gain = {diversity_gains[best_wine]:8.3f} | "
                f"Total utility = {new_total_utility:8.3f} | "
                f"Coverage = {current_coverage}/{max_possible} ({100*current_coverage/max_possible:.1f}%) | "
                f"Tie pool = {len(best_candidates)} wines "
                # f"(quality loss: {tie_analysis['quality_loss_pct']:.2f}%)"
            )

    # Compute final metrics
    total_utility = np.sum(current_utility_per_recipe)

    # Use the utility function to get comprehensive metrics
    metrics = compute_recipe_metrics(U, selected, top_k=top_k)

    return selected, total_utility, metrics


