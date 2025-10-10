"""
data_matrix:

   bm1, bm2, bm3, ...
p1
p2
p3
.

theta_phi:
    theta_mean, theta_std, phi_mean, phi_std
bm1
bm2
bm3
.

stage_post:

    stage1, stage2, stage3, ..., stageN
p1
p2
p3
.

"""



from typing import Tuple
import numpy as np
from numba import njit
from sklearn.cluster import KMeans
from scipy.stats import mode
import re 
import os 
import logging 

def get_two_clusters_with_kmeans(
    bm_measurements: np.ndarray,
    diseased_ids:np.ndarray,
    non_diseased_ids:np.ndarray,
    rng:np.random.Generator,
    max_attempt: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
    """get affected and nonaffected clusters for a biomarker using seeded k-means (semi-supervised KMeans)
    input: 
        - bm_measurements: measurements of all participants for a specific biomarker
        - diseased_arr: an array of 0/1 indicating whether a participant is diseased or not; length is n_participants
        - non_diseased_ids
    output: 
        - A Tuple: two arrays containing the measurements of each cluster (affected, and nonaffected)
        # Note that it is guaranteed that both clusters have at least 2 elements; otherwise, the program will stop. 
    """
    assert len(bm_measurements) == len(diseased_ids) + len(non_diseased_ids), "Biomarker measurements should be of the same length as diseased array"
    # rng = rng.default_rng(seed)
    # rng.seed(seed)

    n_clusters = 2
    measurements = bm_measurements.reshape(-1, 1)

    # Initialize centroids
    healthy_seed = np.mean(measurements[non_diseased_ids])
    diseased_seed = np.mean(measurements[diseased_ids])
    init_centers = np.array([[healthy_seed], [diseased_seed]])

    curr_attempt = 0
    clustering_setup = KMeans(n_clusters=n_clusters, init = init_centers, n_init=1, random_state=42)
    
    while curr_attempt < max_attempt:
        clustering_result = clustering_setup.fit(measurements)
        predictions = clustering_result.labels_
        cluster_counts = np.bincount(predictions) # array([3, 2])
        
        # Exit if exactly two clusters and both have two or more elements
        if len(cluster_counts) == n_clusters and all(c > 1 for c in cluster_counts):
            break 
        curr_attempt += 1
    else:
        print(f"KMeans failed. Will go ahead and randomize the predictions.")
        # Initialize all predictions to -1 (or any placeholder value)
        predictions = np.full(len(measurements), -1)

        # Set all healthy participants to 0
        predictions[non_diseased_ids] = 0

        # Keep trying until both clusters have at least 2 members
        for _ in range(max_attempt):  # try up to 100 times
            # Randomly assign 0 or 1 to non-healthy participants
            predictions[diseased_ids] = rng.choice([0, 1], size=len(diseased_ids))
            cluster_counts = np.bincount(predictions)

            # Check if two non-empty clusters exist:
            if len(cluster_counts) == n_clusters and all(c > 1 for c in cluster_counts):
                break
        else:
            raise ValueError(f"KMeans clustering failed to find valid clusters within max_attempt.")
    
    # labels for healthy participants
    healthy_predictions = predictions[non_diseased_ids]
    # check the label for the majority of healthy participants; that becomes the label for phi cluster
    mode_result = mode(healthy_predictions, keepdims=False).mode
    phi_cluster_idx = mode_result[0] if isinstance(mode_result, np.ndarray) else mode_result
    theta_cluster_idx = 1 - phi_cluster_idx

    # Convert predictions to numpy array if not already
    predictions = np.array(predictions).flatten()

    # Select affected and nonaffected measurements based on cluster index
    theta_measurements = measurements[predictions == theta_cluster_idx].flatten()
    phi_measurements = measurements[predictions == phi_cluster_idx].flatten()

    is_theta = (predictions == theta_cluster_idx).astype(np.float64)

    assert len(is_theta) == len(measurements), "is_theta should have the same length as measurements"

    return np.array(theta_measurements), np.array(phi_measurements), np.array(is_theta)


def get_initial_theta_phi_estimates(
    data_matrix: np.ndarray,
    non_diseased_ids: np.ndarray,
    diseased_ids: np.ndarray,
    prior_n: float,
    prior_v: float,
    rng:np.random.Generator,
) -> np.ndarray:
    """
    Obtain initial theta and phi estimates (mean and standard deviation) for each biomarker.
    (get the clusters using seeded k-means (semi-supervised KMeans);
     estimate the parameters using conjugate priors
    )
    """
    # Number of biomarkers
    N = len(data_matrix[0])
    # Each row is a bm; four cols: theta_mean, theta_std, phi_mean, phi_std
    estimates = np.zeros((N, 4))
    for bm in range(N):
        bm_measurements = data_matrix[:, bm]
        theta_measurements, phi_measurements, _  = get_two_clusters_with_kmeans(
            bm_measurements = bm_measurements, 
            diseased_ids = diseased_ids, 
            non_diseased_ids = non_diseased_ids,
            rng=rng
        )
        # Use MLE to calculate the fallback (also to provide the m0 and s0_sq)
        fallback_params = np.array(
            [np.mean(theta_measurements),
             np.std(theta_measurements, ddof=1),
             np.mean(phi_measurements),
             np.std(phi_measurements, ddof=1)])
        theta_mean, theta_std, phi_mean, phi_std = compute_theta_phi_biomarker_conjugate_priors(
            theta_measurements, phi_measurements, fallback_params, prior_n, prior_v)
        estimates[bm] = np.array([theta_mean, theta_std, phi_mean, phi_std])
    return estimates


@njit
def compute_theta_phi_biomarker_conjugate_priors(
    affected_cluster: np.ndarray,
    non_affected_cluster: np.ndarray,
    theta_phi_current_biomarker: np.ndarray,  # Current state’s θ/φ
    prior_n: float,
    prior_v: float
) -> Tuple[float, float, float, float]:
    """
    When data follows a normal distribution with unknown mean (μ) and unknown variance (σ²),
    the normal-inverse gamma distribution serves as a conjugate prior for these parameters.
    This means the posterior distribution will also be a normal-inverse gamma distribution after updating with observed data.

    Args:
        affected_cluster: list of biomarker measurements
        non_affected_cluster: list of biomarker measurements
        theta_phi_current_biomarker: the current state's theta/phi for this biomarker
        prior_n (strength of belief in prior of mean), and prior_v (prior degree of freedom) are the weakly infomred priors.

    Returns:
        Tuple[float, float, float, float]: Mean and standard deviation for affected (theta) and non-affected (phi) clusters.
    """
    # --- Affected Cluster (Theta) ---
    if len(affected_cluster) < 2:  # Fallback if cluster has 0 or 1 data points
        theta_mean = theta_phi_current_biomarker[0]
        theta_std = theta_phi_current_biomarker[1]
    else:
        theta_mean, theta_std = estimate_params_exact(
            m0=theta_phi_current_biomarker[0],
            # m0=np.mean(affected_cluster),
            n0=prior_n,
            # s0_sq = np.var(affected_cluster, ddof=1),
            s0_sq=theta_phi_current_biomarker[1]**2,
            v0=prior_v,
            data=affected_cluster
        )

    # --- Non-Affected Cluster (Phi) ---
    if len(non_affected_cluster) < 2:  # Fallback if cluster has 0 or 1 data points
        phi_mean = theta_phi_current_biomarker[2]
        phi_std = theta_phi_current_biomarker[3]
    else:
        phi_mean, phi_std = estimate_params_exact(
            m0=theta_phi_current_biomarker[2],
            # m0=np.mean(non_affected_cluster),
            n0=prior_n,
            # s0_sq = np.var(non_affected_cluster, ddof=1),
            s0_sq=theta_phi_current_biomarker[3]**2,
            v0=prior_v,
            data=non_affected_cluster
        )
    return theta_mean, theta_std, phi_mean, phi_std

@njit
def estimate_params_exact(
    m0: float,
    n0: float,
    s0_sq: float,
    v0: float,
    data: np.ndarray
) -> Tuple[float, float]:
    """
    Estimate posterior mean and standard deviation using conjugate priors for a Normal-Inverse Gamma model.

    Args:
        m0 (float): Prior estimate of the mean (μ).
        n0 (float): Strength of the prior belief in m0.
        s0_sq (float): Prior estimate of the variance (σ²).
        v0 (float): Prior degrees of freedom, influencing the certainty of s0_sq.
        data (np.ndarray): Observed data (measurements).

    Returns:
        Tuple[float, float]: Posterior mean (μ) and standard deviation (σ).
    """
    # Data summary
    sample_size = len(data)
    sample_mean = np.mean(data)
    # calculate sample variance
    sum_squared_diff = 0.0 
    for i in range(sample_size):
        diff = data[i] - sample_mean 
        sum_squared_diff += diff * diff 
    # ddof=1 for unbiased estimator
    sample_var = sum_squared_diff/(sample_size - 1)

    # Update hyperparameters for the Normal-Inverse Gamma posterior
    updated_m0 = (n0 * m0 + sample_size * sample_mean) / (n0 + sample_size)
    updated_n0 = n0 + sample_size
    updated_v0 = v0 + sample_size
    updated_s0_sq = (1 / updated_v0) * ((sample_size - 1) * sample_var + v0 * s0_sq +
                                        (n0 * sample_size / updated_n0) * (sample_mean - m0)**2)
    updated_alpha = updated_v0/2
    updated_beta = updated_v0*updated_s0_sq/2

    # Posterior estimates
    mu_posterior_mean = updated_m0
    sigma_squared_posterior_mean = updated_beta/updated_alpha

    mu_estimation = mu_posterior_mean
    std_estimation = np.sqrt(sigma_squared_posterior_mean)

    return mu_estimation, std_estimation

@ njit
def obtain_affected_and_non_clusters(
    bm_measurements:np.ndarray,
    n_participants:int,
    non_diseased_ids:np.ndarray,
    stage_likelihoods_posteriors: np.ndarray,
    disease_stages: np.ndarray,
    curr_order: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Obtain both the affected and non-affected clusters for a single biomarker.

    Args:
        - bm_measurements: all participants' measurements of a specific biomarker 

    Returns:
        Tuple[float, float, float, float]: Mean and standard deviation for affected (theta) and non-affected (phi) clusters.
    """
    affected_cluster = []
    non_affected_cluster = []

    for p in range(n_participants):
        # measurement of p, bm
        m = bm_measurements[p]
        if p in non_diseased_ids:
            non_affected_cluster.append(m)
        else:
            if curr_order == 1:
                affected_cluster.append(m)
            else:
                stage_likelihoods = stage_likelihoods_posteriors[p]
                affected_prob = np.sum(
                    stage_likelihoods[disease_stages >= curr_order])
                non_affected_prob = np.sum(
                    stage_likelihoods[disease_stages < curr_order])
                if affected_prob > non_affected_prob:
                    affected_cluster.append(m)
                elif affected_prob < non_affected_prob:
                    non_affected_cluster.append(m)
                else:
                    if np.random.random() > 0.5:
                        affected_cluster.append(m)
                    else:
                        non_affected_cluster.append(m)
    return np.array(affected_cluster), np.array(non_affected_cluster)

@njit
def update_theta_phi_estimates(
    n_biomarkers:int,
    n_participants:int,
    non_diseased_ids:np.ndarray,
    data_matrix:np.ndarray,
    new_order:np.ndarray,
    theta_phi_current: np.ndarray,  # Current state’s θ/φ
    stage_likelihoods_posteriors: np.ndarray,
    disease_stages: np.ndarray,
    prior_n: float,    # Weak prior (not data-dependent)
    prior_v: float,     # Weak prior (not data-dependent)
) -> np.ndarray:
    """Update theta and phi params for all biomarkers.
    """
    updated_params = np.zeros((n_biomarkers, 4))
    for bm_idx in range(n_biomarkers):
        curr_order = new_order[bm_idx]
        bm_measurements = data_matrix[:,bm_idx]
        theta_phi_current_biomarker = theta_phi_current[bm_idx]
        
        affected_cluster, non_affected_cluster = obtain_affected_and_non_clusters(
            bm_measurements,
            n_participants,
            non_diseased_ids,
            stage_likelihoods_posteriors,
            disease_stages,
            curr_order,
        )
        updated_params[bm_idx, :] = compute_theta_phi_biomarker_conjugate_priors(
            affected_cluster, non_affected_cluster, theta_phi_current_biomarker, prior_n, prior_v)
             
    return updated_params

@njit
def compute_total_ln_likelihood_and_stage_likelihoods(
    n_participants:int,
    data_matrix:np.ndarray,
    new_order:np.ndarray,
    non_diseased_ids: np.ndarray,
    theta_phi: np.ndarray,
    current_pi: np.ndarray,
    disease_stages: np.ndarray,
) -> Tuple[float, np.ndarray]:
    """Calculate the total log likelihood across all participants
        and obtain stage_likelihoods_posteriors
    """
    total_ln_likelihood = 0.0
    
    stage_likelihoods_posteriors = np.zeros((n_participants, len(disease_stages)))

    for participant in range(n_participants):
        measurements = data_matrix[participant]
        if participant in non_diseased_ids:
            ln_likelihood = compute_ln_likelihood(
                measurements, new_order, k_j=0, theta_phi=theta_phi)
        else:
            # Diseased participant (sum over possible stages)
            # ln_stage_likelihoods: N length vector
            ln_stage_likelihoods = np.zeros(len(disease_stages))
            for idx, k_j in enumerate(disease_stages):
                ln_stage_likelihoods[idx] = compute_ln_likelihood(
                    measurements, new_order, k_j=k_j, theta_phi=theta_phi
                ) + np.log(current_pi[idx])
            # Use log-sum-exp trick for numerical stability
            max_ln_likelihood = np.max(ln_stage_likelihoods)
            stage_likelihoods = np.exp(ln_stage_likelihoods - max_ln_likelihood)
            likelihood_sum = np.sum(stage_likelihoods)
            ln_likelihood = max_ln_likelihood + np.log(likelihood_sum)
            
            stage_likelihoods_posteriors[participant] = stage_likelihoods/likelihood_sum

        total_ln_likelihood += ln_likelihood
    return total_ln_likelihood, stage_likelihoods_posteriors


@ njit
def _compute_ln_likelihood_core(measurements, mus, stds):
    """Core computation function optimized with Numba"""
    ln_likelihood = 0.0
    log_two_pi = np.log(2 * np.pi)
    for i in range(len(measurements)):
        var = stds[i] ** 2
        diff = measurements[i] - mus[i]
        # likelihood *= np.exp(-diff**2 / (2 * var)) / np.sqrt(2 * np.pi * var)
        # Log of normal PDF: ln(1/sqrt(2π*var) * exp(-diff²/2var))
        # = -ln(sqrt(2π*var)) - diff²/2var
        ln_likelihood += (-0.5 * (log_two_pi + np.log(var)) -
                          diff**2 / (2 * var))
    return ln_likelihood

@ njit
def compute_ln_likelihood(
    p_measurements: np.ndarray,
    S_n: np.ndarray,
    k_j: int,
    theta_phi: np.ndarray,
) -> float:
    """
    Compute the log likelihood for given participant data.

    Args:
        p_measurements (np.ndarray): Array of measurement values for a specific participant, from bm1 to bmN
        S_n (np.ndarray): the new_order, i.e., the ordering index from bm1 to bmN
        k_j (int): Current stage.
        theta_phi 
    Returns:
        float: Log likelihood value.
    """
    mus = np.zeros(len(p_measurements))
    stds = np.zeros(len(p_measurements))
    affected = k_j >= S_n

    for i in range(len(mus)):
        if affected[i]:
            mus[i] = float(theta_phi[i,0])
            stds[i] = float(theta_phi[i,1])
        else:
            mus[i] = float(theta_phi[i, 2])
            stds[i] = float(theta_phi[i, 3])

    # Apply mask after mus and stds are computed
    valid_mask = (~np.isnan(p_measurements)) & (~np.isnan(mus)) & (stds > 0)
    p_measurements = p_measurements[valid_mask]
    mus = mus[valid_mask]
    stds = stds[valid_mask]

    return _compute_ln_likelihood_core(p_measurements, mus, stds)

def shuffle_order(arr: np.ndarray, n_shuffle: int, rng:np.random.Generator) -> None:
    """
    Randomly shuffle a specified number of elements in an array.

    Args:
    arr (np.ndarray): The array to shuffle elements in.
    n_shuffle (int): The number of elements to shuffle within the array.
    """
    if n_shuffle == 0:
        return
    
    # Select indices and extract elements
    indices = rng.choice(len(arr), size=n_shuffle, replace=False)
    original_indices = indices.copy()

    while True:
        shuffled_indices = rng.permutation(original_indices)
        # Full derangement: make sure no indice stays in its original place
        if not np.any(shuffled_indices == original_indices):
            break
    arr[indices] = arr[shuffled_indices]

def setup_logging(log_file: str):
    """
    Set up logging to a file and console.
    Ensures logs are flushed immediately after each message.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove only the previous handlers while keeping the reference
    while logger.handlers:
        handler = logger.handlers[0]
        handler.close()  # Close the handler to ensure file is properly closed
        logger.removeHandler(handler)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='w')  # Use 'w' mode to start fresh
    file_handler.setLevel(logging.INFO)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def extract_fname(data_file:str) -> str:
    """
    Extract the base filename (without extension) from the data file path.
    Replace invalid characters (e.g., `|`) with underscores.
    """
    base_name = data_file.split('/')[-1]
    fname = base_name.split(".csv")[0]
    fname = re.sub(r'[\\|/:"*?<>]+', '_', fname)
    return fname 

def cleanup_old_files(output_dir: str, fname: str):
    """
    Remove old files (heatmap, traceplot, results, log) for the given fname.
    Logs a warning if files do not exist.
    """
    files_to_remove = [
        f"{output_dir}/heatmaps/{fname}_heatmap.png",
        f"{output_dir}/traceplots/{fname}_traceplot.png",
        f"{output_dir}/results/{fname}_results.json",
        f"{output_dir}/logs/{fname}.log"
    ]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Removed old file: {file_path}")
            except Exception as e:
                logging.error(f"Error removing old file: {file_path}: {e}")
        else:
            logging.warning(f"File does not exist, skipping removal: {file_path}")

@njit
def compute_unbiased_stage_likelihoods(
    n_participants:int,
    data_matrix:np.ndarray,
    new_order:np.ndarray,
    theta_phi: np.ndarray,
    updated_pi: np.ndarray,
    n_stages = int,
) -> np.ndarray:
    """Calculate the total log likelihood across all participants
        and obtain stage_likelihoods_posteriors
    """
    stage_likelihoods_posteriors = np.zeros((n_participants, n_stages))

    for participant in range(n_participants):
        measurements = data_matrix[participant]
        # ln_stage_likelihoods: N length vector
        ln_stage_likelihoods = np.ones(n_stages)
        for k_j in range(n_stages):
            ln_stage_likelihoods[k_j] = compute_ln_likelihood(
                measurements, new_order, k_j=k_j, theta_phi=theta_phi
            ) + np.log(updated_pi[k_j])
        # Use log-sum-exp trick for numerical stability
        max_ln_likelihood = np.max(ln_stage_likelihoods)
        stage_likelihoods = np.exp(
            ln_stage_likelihoods - max_ln_likelihood)
        likelihood_sum = np.sum(stage_likelihoods)
        stage_likelihoods_posteriors[participant] = stage_likelihoods/likelihood_sum

    return stage_likelihoods_posteriors
