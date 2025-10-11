import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from librosa.sequence import dtw
from scipy.signal import savgol_filter, medfilt
import matplotlib.patches as patches
from matplotlib import cm
from shapely.geometry import Polygon, MultiPolygon
from scipy.spatial import cKDTree
from scipy.interpolate import splprep, splev, UnivariateSpline
from scipy.optimize import minimize_scalar
import pandas as pd
from tqdm import trange
from librosa.sequence import dtw

def convert_to_uint8(channel):
    """
    Convert a normalized float array to uint8 format.
    
    This function takes an array with values between 0 and 1 and
    converts it to uint8 format by scaling values to the range 0-255.
    
    Parameters
    ----------
    channel : numpy.ndarray
        Input array with normalized values (typically between 0 and 1).
        
    Returns
    -------
    numpy.ndarray
        Array converted to uint8 data type with values scaled to 0-255 range.
    """
    channel8 = channel * 255
    channel8 = channel8.astype('uint8')
    return channel8

def normalized_difference(b1, b2):
    """
    Calculate the normalized difference between two bands.

    This function computes the normalized difference index, a common
    calculation in remote sensing (e.g., NDVI, NDWI). It handles cases
    where both input bands are zero by setting the corresponding output
    pixels to NaN to avoid division by zero and undefined results.

    Parameters
    ----------
    b1 : numpy.ndarray
        The first input band (e.g., Near Infrared for NDVI).
        Should be a 2D NumPy array of numerical type.
    b2 : numpy.ndarray
        The second input band (e.g., Red for NDVI).
        Should be a 2D NumPy array of the same shape and numerical type as b1.

    Returns
    -------
    numpy.ndarray
        A 2D NumPy array containing the normalized difference values.
        The values typically range from -1 to 1. Pixels where both
        input bands were zero will be NaN.
    """
    band1 = np.where((b1==0) & (b2==0), np.nan, b1)
    band2 = np.where((b1==0) & (b2==0), np.nan, b2)
    return (band1 - band2) / (band1 + band2)

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def find_condition(condition):
    """
    Find the indices of elements that are non-zero in the flattened input array.

    Parameters
    ----------
    condition : array_like
        Input array. The function will find the non-zero elements in this array.

    Returns
    -------
    res : ndarray
        Indices of elements that are non-zero in the flattened input array.
    """
    res, = np.nonzero(np.ravel(condition))
    return res

def count_vertices(geometry):
    """Count total number of vertices in a geometry"""
    
    if isinstance(geometry, Polygon):
        count = len(geometry.exterior.coords)
        for interior in geometry.interiors:
            count += len(interior.coords)
        return count
    elif isinstance(geometry, MultiPolygon):
        return sum(count_vertices(poly) for poly in geometry.geoms)
    else:
        return 0

def remove_endpoints(poly_sm, remove_count=3):
    """
    remove problematic start/end points
    """
    x, y = poly_sm.xy
    x, y = np.array(x), np.array(y)
    
    # Remove first and last few points
    x_trimmed = x[remove_count:-remove_count]
    y_trimmed = y[remove_count:-remove_count]
    
    # Close the polygon
    x_result = np.append(x_trimmed, x_trimmed[0])
    y_result = np.append(y_trimmed, y_trimmed[0])
    
    return x_result, y_result

def find_numbers_between(start, end, decimal_places):
    """
    Returns a list of numbers between start and end, rounded to the specified decimal places.

    Parameters
    ----------
    start : float
        The starting number of the range.
    end : float
        The ending number of the range.
    decimal_places : int
        The number of decimal places to round each number to.

    Returns
    -------
    list of float
        A list of numbers between start and end, inclusive, rounded to the specified decimal places.
    """
    step = 10 ** -decimal_places  # Calculate the step size based on decimal places
    numbers = []
    current_number = round(start, decimal_places)  # Begin with start rounded to specified places
    while current_number <= end:
        numbers.append(current_number)
        current_number += step  # Increment by the step size
        current_number = round(current_number, decimal_places)
    return numbers

def resample_and_smooth(x, y, delta_s, smoothing_factor, compute_curvature=False):
    """
    Resample and smooth a given set of points, optionally computing curvature.

    Parameters
    ----------
    x : array_like
        The x-coordinates of the points.
    y : array_like
        The y-coordinates of the points.
    delta_s : float
        The desired spacing between resampled points.
    smoothing_factor : float
        The smoothing factor used in the spline fitting.
    compute_curvature : bool, optional
        If True, also compute curvature at each resampled point. Default is False.

    Returns
    -------
    xs : ndarray
        The x-coordinates of the resampled and smoothed points.
    ys : ndarray
        The y-coordinates of the resampled and smoothed points.
    curvature : ndarray, optional
        The curvature values at each resampled point. Only returned if compute_curvature=True.

    Notes
    -----
    This function uses a parametric spline representation to smooth and resample the input points.
    If compute_curvature=True, curvature is calculated using spline derivatives, which is more
    accurate and stable than finite difference methods, especially for noisy data.
    If the spline fitting fails, the original points are returned (and None for curvature if requested).
    """
    x = np.array(x)
    y = np.array(y)
    okay = np.where(np.abs(np.diff(x)) + np.abs(np.diff(y)) > 0)
    dx = np.diff(x[okay]); dy = np.diff(y[okay])
    ds = np.sqrt(dx**2+dy**2)
    try:
        tck, u = scipy.interpolate.splprep([x[okay], y[okay]], s=smoothing_factor) # parametric spline representation of curve
    except:
        if compute_curvature:
            return x, y, None
        else:
            return x, y
    
    unew = np.linspace(0,1,1+int(sum(ds)/delta_s)) # vector for resampling
    out = scipy.interpolate.splev(unew,tck) # resampling
    xs = out[0]
    ys = out[1]
    
    if compute_curvature:
        # Compute curvature using spline derivatives
        # Get first derivatives (dx/du, dy/du)
        dx_du, dy_du = scipy.interpolate.splev(unew, tck, der=1)
        
        # Get second derivatives (d²x/du², d²y/du²)
        d2x_du2, d2y_du2 = scipy.interpolate.splev(unew, tck, der=2)
        
        # Calculate curvature using the formula: κ = (x'y'' - y'x'') / (x'² + y'²)^(3/2)
        # Note: this gives curvature with respect to the parameter u, which is what we want
        numerator = dx_du * d2y_du2 - dy_du * d2x_du2
        denominator = np.power(dx_du**2 + dy_du**2, 1.5)
        
        # Avoid division by zero
        denominator = np.where(denominator == 0, np.finfo(float).eps, denominator)
        curvature = numerator / denominator
        
        return xs, ys, curvature
    else:
        return xs, ys

def compute_s_distance(x, y):
    """
    Compute the first derivatives of a curve (centerline) and the cumulative distance along the curve.

    Parameters
    ----------
    x : array_like
        Cartesian x-coordinates of the curve.
    y : array_like
        Cartesian y-coordinates of the curve.

    Returns
    -------
    s : ndarray
        Cumulative distance along the curve.

    Notes
    -----
    The function calculates the first derivatives of the x and y coordinates using numpy's gradient function.
    It then computes the distances between consecutive points along the curve and the cumulative distance.
    """
    dx = np.gradient(x) # first derivatives
    dy = np.gradient(y)   
    ds = np.sqrt(dx**2+dy**2)
    s = np.hstack((0, np.cumsum(ds[1:])))
    return s

def find_closest_negative_minimum(data, bins=256, sigma=5, plot_result=False):
    """
    Find the local minimum in a distribution closest to zero on the negative side.
    This method first bins the data into a histogram and then applies a smoothing filter to the histogram counts.

    Args:
        data (np.ndarray): A 1D array of numbers (e.g., NDWI values).
        bins (int): The number of bins for the histogram. More bins provide more detail but may be noisier.
        sigma (float): The standard deviation for the Gaussian filter used to smooth the histogram.
                       Larger values result in a smoother curve.
        plot_result (bool): If True, a plot visualizing the process will be shown.

    Returns:
        float or None: The value of the minimum closest to zero on the negative side.
                       Returns None if no negative minima are found.
    """
    # 1. Create a histogram of the data. This is much faster than KDE.
    data = data[data!=0]
    counts, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # 2. Smooth the histogram counts with a 1D Gaussian filter.
    smoothed_counts = gaussian_filter1d(counts, sigma=sigma)

    # 3. Find the minima by finding the peaks of the inverted, smoothed counts.
    minima_indices, _ = find_peaks(-smoothed_counts)
    minima_x = bin_centers[minima_indices]
    
    # 4. Filter for minima that are on the negative side of zero.
    negative_minima = minima_x[minima_x < 0]

    # 5. If no negative minima were found, return None.
    if len(negative_minima) == 0:
        print("No negative minima found.")
        return None

    # 6. From the negative minima, find the one closest to zero.
    closest_minimum = np.max(negative_minima)
    
    # 7. (Optional) Plot the results for verification.
    if plot_result:
        plt.figure(figsize=(12, 7))
        plt.hist(data, bins=bins, density=True, alpha=0.5, label='NDWI Data Histogram')
        plt.plot(bin_centers, smoothed_counts, lw=2, label='Smoothed Histogram PDF')
        plt.plot(minima_x, smoothed_counts[minima_indices], 'x', color='red', markersize=10, label='All Local Minima')
        plt.axvline(closest_minimum, color='green', linestyle='--', lw=2, label=f'Closest Negative Minimum: {closest_minimum:.2f}')
        plt.title('Distribution with Smoothed Histogram and Identified Minimum')
        plt.xlabel('NDWI Value')
        plt.ylabel('Density')
        plt.legend()
        plt.grid(True, linestyle=':')
        plt.show()

    return closest_minimum

def visualize_curvature_circles(x, y, curvature, xs, ys, curvature_threshold=0.001, 
                               skip_points=2, ax=None, show_all_points=True, 
                               use_percentile_selection=True, bend_percentile=50,
                               colormap='plasma', curv_min=None, curv_max=None,
                               river_color='b'):
    """
    Visualize curvature by plotting circles of curvature for high-curvature points.
    
    This function helps validate curvature calculations by drawing circles with
    radius R = 1/|curvature| that should be tangent to the centerline at each point.
    Circles are color-coded by curvature magnitude and can be filtered by percentile.
    
    Parameters
    ----------
    x : array_like
        Original x-coordinates of the centerline.
    y : array_like
        Original y-coordinates of the centerline.
    curvature : array_like
        Computed curvature values at resampled points.
    xs : array_like
        Resampled x-coordinates (same length as curvature).
    ys : array_like
        Resampled y-coordinates (same length as curvature).
    curvature_threshold : float, optional
        Minimum absolute curvature value to consider. Default is 0.001.
    skip_points : int, optional
        Plot every nth point to avoid overcrowding. Default is 2.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates new figure.
    show_all_points : bool, optional
        If True, show all centerline points. Default is True.
    use_percentile_selection : bool, optional
        If True, select points based on percentile within each bend. Default is True.
    bend_percentile : float, optional
        Percentile threshold for selecting points within bends (0-100). Default is 50.
    colormap : str, optional
        Colormap for color-coding curvature magnitude. Default is 'plasma'.
    curv_min : float, optional
        Minimum curvature value for color-coding. Default is 0.00001.
    curv_max : float, optional
        Maximum curvature value for color-coding. Default is 0.001.
    
    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object with the plot.
    fig : matplotlib.figure.Figure
        The figure object (only if ax was None).
        
    Notes
    -----
    The circles are plotted on the "inside" of the curve (concave side) for positive
    curvature and "outside" (convex side) for negative curvature, following the
    convention where positive curvature means curving to the left.
    
    Color coding: Higher curvature = more vivid colors and less transparency.
    Percentile selection: Only shows points above the specified percentile within each bend.
    """
    
    create_fig = ax is None
    if create_fig:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    else:
        fig = None
    
    # Plot the original centerline with low z-order (background)
    if show_all_points:
        ax.plot(x, y, 'k.', alpha=0.3, markersize=3, label='Original points', zorder=1)
    
    # Enhanced point selection based on method
    if use_percentile_selection:
        selected_indices = _select_bend_percentile_points(curvature, curvature_threshold, 
                                                        bend_percentile, skip_points)
    else:
        # Original method: simple threshold + skip
        high_curv_mask = np.abs(curvature) > curvature_threshold
        high_curv_indices = np.where(high_curv_mask)[0]
        selected_indices = high_curv_indices[::skip_points]
    
    total_high_curv = np.sum(np.abs(curvature) > curvature_threshold)
    print(f"Plotting curvature circles for {len(selected_indices)} points")
    print(f"(out of {total_high_curv} points above threshold)")
    
    if len(selected_indices) == 0:
        print("No points selected for visualization")
        if create_fig:
            return ax, fig
        else:
            return ax
    
    # Compute tangent vectors at each point for circle positioning
    dx = np.gradient(xs)
    dy = np.gradient(ys)
    
    # Normalize tangent vectors
    ds = np.sqrt(dx**2 + dy**2)
    dx_norm = dx / ds
    dy_norm = dy / ds
    
    # Normal vectors (perpendicular to tangent, pointing "inward" for positive curvature)
    nx = -dy_norm  # perpendicular to tangent
    ny = dx_norm
    
    # Set up color mapping for curvature magnitude
    selected_curvatures = np.abs(curvature[selected_indices])
    if len(selected_curvatures) > 0:
        if curv_min is None:
            curv_min = np.min(selected_curvatures)
        if curv_max is None:
            curv_max = np.max(selected_curvatures)
        curv_range = curv_max - curv_min if curv_max > curv_min else 1.0
        
        # Get colormap
        cmap = cm.get_cmap(colormap)
        
    # Prepare circle data for z-order sorting
    circle_data = []
    
    for i in selected_indices:
        if i >= len(curvature) or i >= len(xs) or i >= len(ys):
            continue
            
        curv = curvature[i]
        if abs(curv) < curvature_threshold:
            continue
            
        # Radius of curvature
        radius = 1.0 / abs(curv)
        
        # Color coding based on curvature magnitude
        curv_normalized = (abs(curv) - curv_min) / curv_range if curv_range > 0 else 0.5
        if curv_normalized > 1:
            curv_normalized = 1.0
        color = cmap(curv_normalized)
        
        # Center point coordinates
        # For positive curvature (left turn), center is to the right of motion direction
        # For negative curvature (right turn), center is to the left of motion direction
        if curv > 0:
            # Positive curvature: center is on the right side (normal direction)
            center_x = xs[i] + radius * nx[i]
            center_y = ys[i] + radius * ny[i]
        else:
            # Negative curvature: center is on the left side (opposite normal direction)
            center_x = xs[i] - radius * nx[i]
            center_y = ys[i] - radius * ny[i]
        
        # Store circle data for sorting
        circle_data.append({
            'center_x': center_x,
            'center_y': center_y,
            'radius': radius,
            'color': color,
            'curvature': abs(curv),
            'curvature_normalized': curv_normalized,
            'point_x': xs[i],
            'point_y': ys[i],
        })
    
    # Sort circles by curvature magnitude (ascending order)
    # This way, largest curvature (smallest radius) circles are drawn last (on top)
    circle_data.sort(key=lambda x: x['curvature'])
    
    circles_plotted = 0
    
    # Draw circles in z-order: lowest curvature first, highest curvature last (on top)
    for circle_info in circle_data:
        # Calculate z-order: higher curvature = higher z-order
        zorder = 10 + int(circle_info['curvature'] * 1000)  # Scale for integer z-order
        
        # Create circle with z-order
        circle = patches.Circle((circle_info['center_x'], circle_info['center_y']), 
                              circle_info['radius'], 
                              fill=True, color=circle_info['color'], alpha=circle_info['curvature_normalized'], 
                              linewidth=1.5, linestyle='-', zorder=zorder)
        ax.add_patch(circle)
        
        # Mark the centerline point with same z-order
        # ax.plot(circle_info['point_x'], circle_info['point_y'], 'o', 
        #        color=circle_info['color'], markersize=6, zorder=zorder+1)
        
        circles_plotted += 1
    
    # Create colorbar
    if len(selected_indices) > 0:
            sm = plt.cm.ScalarMappable(cmap=cmap, 
                                     norm=plt.Normalize(vmin=curv_min, vmax=curv_max))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.8, pad=0.02)
            cbar.set_label('|Curvature|', rotation=270, labelpad=15)

    # Plot the smoothed centerline with low z-order (background)
    ax.plot(xs, ys, color=river_color, linewidth=2, alpha=1.0, label='Smoothed centerline', zorder=zorder+1)
    
    ax.set_aspect('equal')
    # ax.legend()
    
    # Enhanced title with method information
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    
    print(f"Plotted {circles_plotted} curvature circles")
    if len(selected_indices) > 0:
        print(f"Curvature range: {curv_min:.5f} to {curv_max:.5f}")
    
    if create_fig:
        return ax, fig
    else:
        return ax

def _select_bend_percentile_points(curvature, curvature_threshold, bend_percentile, skip_points):
    """
    Select points based on percentile within individual bends rather than global threshold.
    
    This function identifies individual bends (continuous regions of same-sign curvature)
    and selects only the points that exceed the specified percentile within each bend.
    
    Parameters
    ----------
    curvature : array_like
        Computed curvature values.
    curvature_threshold : float
        Minimum absolute curvature to consider a region as a "bend".
    bend_percentile : float
        Percentile threshold within each bend (0-100).
    skip_points : int
        Skip factor for reducing point density.
    
    Returns
    -------
    selected_indices : ndarray
        Indices of selected points for visualization.
    """
    curvature = np.array(curvature)
    n_points = len(curvature)
    
    # Find regions that exceed the base threshold
    above_threshold = np.abs(curvature) > curvature_threshold
    
    if not np.any(above_threshold):
        return np.array([], dtype=int)
    
    # Identify individual bends (continuous regions of same-sign curvature)
    sign_changes = np.diff(np.sign(curvature))
    bend_boundaries = np.where(np.abs(sign_changes) > 0)[0] + 1
    bend_boundaries = np.concatenate(([0], bend_boundaries, [n_points]))
    
    selected_indices = []
    
    for i in range(len(bend_boundaries) - 1):
        start_idx = bend_boundaries[i]
        end_idx = bend_boundaries[i + 1]
        
        # Extract this bend segment
        bend_curvature = curvature[start_idx:end_idx]
        bend_abs_curvature = np.abs(bend_curvature)
        
        # Only consider this bend if it has points above threshold
        bend_above_threshold = bend_abs_curvature > curvature_threshold
        
        if not np.any(bend_above_threshold):
            continue
        
        # Find percentile threshold for this bend
        bend_threshold_curv = bend_abs_curvature[bend_above_threshold]
        
        if len(bend_threshold_curv) == 0:
            continue
            
        percentile_threshold = np.percentile(bend_threshold_curv, bend_percentile)
        
        # Select points in this bend that exceed the percentile threshold
        bend_selected_mask = bend_abs_curvature >= percentile_threshold
        bend_selected_indices = np.where(bend_selected_mask)[0] + start_idx
        
        # Apply skip_points to reduce density
        if len(bend_selected_indices) > 0:
            bend_selected_indices = bend_selected_indices[::skip_points]
            selected_indices.extend(bend_selected_indices)
    
    return np.array(selected_indices, dtype=int)

def correlate_curves(x1,x2,y1,y2,band_rad=None):
    """ 
    Use dynamic time warping to correlate two 2D curves.

    Parameters
    ----------
    x1 : 1D array
        x-coordinates of first curve.
    x2 : 1D array
        x-coordinates of second curve.
    y1 : 1D array
        y-coordinates of first curve.
    y2 : 1D array
        y-coordinates of second curve.

    Returns
    -------
    p : 1D array
        Correlation indices for first curve.
    q : 1D array
        correlation indices for second curve
    """

    X = np.vstack((x1,y1))
    Y = np.vstack((x2,y2))
    D, wp = dtw(X, Y, band_rad=band_rad)
    p = wp[:,0] # correlation indices for first curve
    q = wp[:,1] # correlation indices for second curve
    return p, q, D

def visualize_dtw_correlations(x1, y1, x2, y2, p, q, ax=None, 
                              show_all_connections=True, connection_step=1,
                              connection_alpha=0.3, connection_color='gray',
                              centerline_colors=('blue', 'red')):
    """
    Visualize DTW (Dynamic Time Warping) correlation results by plotting connecting lines
    between corresponding points on two centerlines and compute signed distances.
    
    Parameters
    ----------
    x1, y1 : array_like
        Coordinates of the first centerline.
    x2, y2 : array_like
        Coordinates of the second centerline.
    p, q : array_like
        DTW correlation indices. p[i] corresponds to q[i], meaning point p[i] 
        on centerline 1 corresponds to point q[i] on centerline 2.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, creates new figure.
    show_all_connections : bool, optional
        If True, shows all connection lines. If False, uses connection_step. Default is True.
    connection_step : int, optional
        Show every nth connection line to reduce clutter. Default is 1.
    connection_alpha : float, optional
        Transparency of connection lines. Default is 0.3.
    connection_color : str, optional
        Color of connection lines. Default is 'gray'.
    centerline_colors : tuple, optional
        Colors for the two centerlines. Default is ('blue', 'red').
    
    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object with the plot.
    fig : matplotlib.figure.Figure
        The figure object (only if ax was None).
        
    Examples
    --------
    >>> # After running DTW correlation
    >>> p, q, cost = correlate_curves(x1, x2, y1, y2)
    >>> ax, fig = visualize_dtw_correlations(x1, y1, x2, y2, p, q, connection_step=5)
    >>> # To get distances separately:
    >>> distances, valid_mask = compute_migration_distances(x1, y1, x2, y2, p, q)
    """
    
    # Convert inputs to numpy arrays
    x1, y1 = np.array(x1), np.array(y1)
    x2, y2 = np.array(x2), np.array(y2)
    p, q = np.array(p), np.array(q)
    
    create_fig = ax is None
    if create_fig:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    else:
        fig = None
    
    # Plot the two centerlines
    ax.plot(x1, y1, color=centerline_colors[0], linewidth=2, alpha=0.8, 
           label=f'Centerline 1 ({len(x1)} points)', marker='o', markersize=3, zorder=3)
    ax.plot(x2, y2, color=centerline_colors[1], linewidth=2, alpha=0.8, 
        label=f'Centerline 2 ({len(x2)} points)', marker='s', markersize=3, zorder=3)
     
    # Compute signed distances and average by x1 point index
    # Create arrays to store distances for each x1 point
    distances_by_x1_point = [[] for _ in range(len(x1))]
    
    for i in range(len(p)):
        # Get corresponding point indices
        p_idx = p[i]
        q_idx = q[i]
        
        # Check bounds
        if p_idx < len(x1) and q_idx < len(x2):
            # Get coordinates of corresponding points
            x1_point, y1_point = x1[p_idx], y1[p_idx]
            x2_point, y2_point = x2[q_idx], y2[q_idx]
            
            # Compute signed distance based on position relative to centerline 1
            # Need to determine the downstream direction at this point
            
            # Get tangent vector at current point (downstream direction)
            if p_idx == 0:
                # Use forward difference for first point
                if len(x1) > 1:
                    tx = x1[p_idx + 1] - x1[p_idx]
                    ty = y1[p_idx + 1] - y1[p_idx]
                else:
                    tx, ty = 1.0, 0.0  # fallback
            elif p_idx == len(x1) - 1:
                # Use backward difference for last point
                tx = x1[p_idx] - x1[p_idx - 1]
                ty = y1[p_idx] - y1[p_idx - 1]
            else:
                # Use central difference for interior points
                tx = x1[p_idx + 1] - x1[p_idx - 1]
                ty = y1[p_idx + 1] - y1[p_idx - 1]
            
            # Normalize tangent vector
            t_mag = np.sqrt(tx**2 + ty**2)
            if t_mag > 0:
                tx /= t_mag
                ty /= t_mag
            else:
                tx, ty = 1.0, 0.0  # fallback for degenerate case
            
            # Compute normal vector (perpendicular to tangent, pointing left)
            # For a tangent vector (tx, ty), the left normal is (-ty, tx)
            nx = -ty
            ny = tx
            
            # Vector from centerline 1 point to centerline 2 point
            dx = x2_point - x1_point
            dy = y2_point - y1_point
            
            # Compute signed distance using dot product with normal vector
            # Positive when point is to the left of centerline 1 (looking downstream)
            signed_distance = dx * nx + dy * ny
            
            # Add to the list for this x1 point
            distances_by_x1_point[p_idx].append(signed_distance)
    
    # Average distances for each x1 point (NaN if no correspondences)
    distances = np.full(len(x1), np.nan)
    valid_correspondences = []
    
    for i in range(len(x1)):
        if len(distances_by_x1_point[i]) > 0:
            distances[i] = np.mean(distances_by_x1_point[i])
            valid_correspondences.append(i)
    
    # Determine which connections to show for visualization
    # We need to go back to the original p, q indices for drawing connections
    if show_all_connections:
        indices_to_show = range(0, len(p), connection_step)
    else:
        # Show evenly spaced connections
        n_connections = min(50, len(p) // connection_step)
        indices_to_show = np.linspace(0, len(p)-1, n_connections, dtype=int)
    
    print(f"Showing {len(indices_to_show)} connection lines out of {len(p)} total correspondences")
    print(f"Valid x1 points with distances: {len(valid_correspondences)} out of {len(x1)}")
    
    # Draw connection lines for selected indices
    for idx in indices_to_show:
        if idx >= len(p) or idx >= len(q):
            continue
            
        p_idx = p[idx]
        q_idx = q[idx]
        
        # Check bounds
        if p_idx >= len(x1) or q_idx >= len(x2):
            continue
        
        # Get coordinates of corresponding points
        x1_point, y1_point = x1[p_idx], y1[p_idx]
        x2_point, y2_point = x2[q_idx], y2[q_idx]
        
        # Draw connection line
        ax.plot([x1_point, x2_point], [y1_point, y2_point], 
               color=connection_color, alpha=connection_alpha, linewidth=1, 
               linestyle='-', zorder=1)
    
    # Highlight start and end points
    ax.plot(x1[0], y1[0], 'o', color=centerline_colors[0], markersize=8, 
           markeredgecolor='black', markeredgewidth=2, label='Start 1', zorder=5)
    ax.plot(x1[-1], y1[-1], 's', color=centerline_colors[0], markersize=8, 
           markeredgecolor='black', markeredgewidth=2, label='End 1', zorder=5)
    ax.plot(x2[0], y2[0], 'o', color=centerline_colors[1], markersize=8, 
           markeredgecolor='black', markeredgewidth=2, label='Start 2', zorder=5)
    ax.plot(x2[-1], y2[-1], 's', color=centerline_colors[1], markersize=8, 
           markeredgecolor='black', markeredgewidth=2, label='End 2', zorder=5)
    
    # Set up the plot
    ax.set_aspect('equal')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    
    # Enhanced title with statistics
    # Use only valid (non-NaN) distances for statistics
    valid_distances = distances[~np.isnan(distances)]
    total_correspondences = len(p)
    valid_points = len(valid_correspondences)
    connections_shown = len(indices_to_show)
    mean_distance = np.mean(valid_distances) if len(valid_distances) > 0 else 0
    abs_max_distance = np.max(np.abs(valid_distances)) if len(valid_distances) > 0 else 0
    
    title = f'DTW Correlation Visualization\n{total_correspondences} correspondences → {valid_points} x1 points'
    title += f'\nMean signed distance: {mean_distance:.2f}, Max |distance|: {abs_max_distance:.2f}'
    
    ax.set_title(title)
    
    # Print summary statistics
    print(f"DTW Correlation Summary:")
    print(f"  Total DTW correspondences: {total_correspondences}")
    print(f"  Unique x1 points with distances: {valid_points}")
    print(f"  Connections displayed: {connections_shown}")
    print(f"  Signed distance statistics (averaged by x1 point):")
    print(f"    Mean: {mean_distance:.2f}")
    print(f"    Median: {np.median(valid_distances):.2f}" if len(valid_distances) > 0 else "    Median: N/A")
    print(f"    Std: {np.std(valid_distances):.2f}" if len(valid_distances) > 0 else "    Std: N/A")
    print(f"    Min: {np.min(valid_distances):.2f}" if len(valid_distances) > 0 else "    Min: N/A")
    print(f"    Max: {np.max(valid_distances):.2f}" if len(valid_distances) > 0 else "    Max: N/A")
    print(f"    Max |distance|: {abs_max_distance:.2f}")
    
    if create_fig:
        return ax, fig
    else:
        return ax


def resample_channel_width_to_centerline(x_orig, y_orig, width_orig, x_smooth, y_smooth, 
                                        method='nearest_neighbor', max_distance=None):
    """
    Resample channel width data from original centerline points to smoothed centerline points.
    
    This function handles the spatial correspondence between original and smoothed centerlines
    more robustly than along-channel distance interpolation.
    
    Parameters
    ----------
    x_orig, y_orig : array_like
        Coordinates of the original centerline points where width was measured.
    width_orig : array_like
        Channel width values at the original centerline points.
    x_smooth, y_smooth : array_like
        Coordinates of the smoothed/resampled centerline points.
    method : str, optional
        Resampling method. Options: 'nearest_neighbor', 'inverse_distance', 'spline_projection'.
        Default is 'nearest_neighbor'.
    max_distance : float, optional
        Maximum distance for considering a match (for quality control).
        If None, uses 3 times the mean spacing of original points.
    
    Returns
    -------
    width_resampled : numpy.ndarray
        Channel width values resampled to the smoothed centerline points.
    distances : numpy.ndarray
        Distance from each smooth point to its matched original point (for quality assessment).
    
    Examples
    --------
    >>> # Get smoothed centerline and curvature
    >>> x_smooth, y_smooth, curvature = resample_and_smooth(x_orig, y_orig, delta_s=5, 
    ...                                                     smoothing_factor=1e6, 
    ...                                                     compute_curvature=True)
    >>> # Resample width to match smoothed centerline
    >>> width_smooth, match_distances = resample_channel_width_to_centerline(
    ...     x_orig, y_orig, width_orig, x_smooth, y_smooth)
    """
    
    # Convert to numpy arrays
    x_orig, y_orig = np.array(x_orig), np.array(y_orig)
    width_orig = np.array(width_orig)
    x_smooth, y_smooth = np.array(x_smooth), np.array(y_smooth)
    
    # Calculate default max_distance if not provided
    if max_distance is None:
        # Use 3 times the mean spacing of original points
        orig_spacing = np.mean(np.sqrt(np.diff(x_orig)**2 + np.diff(y_orig)**2))
        max_distance = 3 * orig_spacing
    
    if method == 'nearest_neighbor':
        # Build KD-tree for fast nearest neighbor search
        tree = cKDTree(np.column_stack([x_orig, y_orig]))
        
        # Find nearest original point for each smooth point
        distances, indices = tree.query(np.column_stack([x_smooth, y_smooth]))
        
        # Use width from nearest neighbor
        width_resampled = width_orig[indices]
        
        # Mark points that are too far as invalid
        if max_distance is not None:
            far_mask = distances > max_distance
            if np.any(far_mask):
                print(f"Warning: {np.sum(far_mask)} points exceed max_distance ({max_distance:.1f})")
                width_resampled[far_mask] = np.nan
        
        return width_resampled, distances
        
    elif method == 'inverse_distance':
        # Inverse distance weighted interpolation
        width_resampled = np.zeros(len(x_smooth))
        distances = np.zeros(len(x_smooth))
        
        for i, (xs, ys) in enumerate(zip(x_smooth, y_smooth)):
            # Calculate distances to all original points
            dists = np.sqrt((x_orig - xs)**2 + (y_orig - ys)**2)
            
            # Find points within max_distance
            valid_mask = dists <= max_distance if max_distance else np.ones_like(dists, dtype=bool)
            
            if np.any(valid_mask):
                valid_dists = dists[valid_mask]
                valid_widths = width_orig[valid_mask]
                
                # Avoid division by zero for exact matches
                valid_dists = np.maximum(valid_dists, 1e-10)
                
                # Inverse distance weights
                weights = 1.0 / valid_dists**2
                weights /= np.sum(weights)
                
                # Weighted average
                width_resampled[i] = np.sum(weights * valid_widths)
                distances[i] = np.min(valid_dists)
            else:
                width_resampled[i] = np.nan
                distances[i] = np.inf
        
        return width_resampled, distances
        
    elif method == 'spline_projection':
        # Project smooth points onto original centerline and interpolate
        try:
            # Create parametric spline for original centerline
            tck_orig, u_orig = splprep([x_orig, y_orig], s=0)  # No smoothing, exact fit
            
            # Create spline for width along original centerline parameter
            width_spline = UnivariateSpline(u_orig, width_orig, s=0)  # Exact fit
            
            width_resampled = np.zeros(len(x_smooth))
            distances = np.zeros(len(x_smooth))
            
            for i, (xs, ys) in enumerate(zip(x_smooth, y_smooth)):
                # Find parameter value on original spline closest to smooth point
                # Use optimization to find closest point
                
                def distance_to_point(u_val):
                    if u_val < 0:
                        u_val = 0
                    elif u_val > 1:
                        u_val = 1
                    point = splev(u_val, tck_orig)
                    return (point[0] - xs)**2 + (point[1] - ys)**2
                
                result = minimize_scalar(distance_to_point, bounds=(0, 1), method='bounded')
                best_u = result.x
                
                # Get width at this parameter value
                width_resampled[i] = width_spline(best_u)
                
                # Calculate actual distance for quality assessment
                closest_point = splev(best_u, tck_orig)
                distances[i] = np.sqrt((closest_point[0] - xs)**2 + (closest_point[1] - ys)**2)
            
            return width_resampled, distances
            
        except Exception as e:
            print(f"Spline projection failed: {e}")
            print("Falling back to nearest neighbor method")
            return resample_channel_width_to_centerline(x_orig, y_orig, width_orig, 
                                                       x_smooth, y_smooth, 
                                                       method='nearest_neighbor', 
                                                       max_distance=max_distance)
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'nearest_neighbor', 'inverse_distance', or 'spline_projection'")


def get_width_and_curvature(river, delta_s=5, smoothing_factor=1e6, 
                                    width_method='nearest_neighbor', curvature_smoothing=True,
                                    savgol_factor=11):
    """
    Get width and curvature from a river object at a given along-channel sampling distance.
    
    Parameters
    ----------
    river : River object
        River object with main_path and _D_primal attributes.
    delta_s : float, optional
        Resampling distance for smooth centerline. Default is 5.
    smoothing_factor : float, optional
        Smoothing factor for spline. Default is 1e6.
    width_method : str, optional
        Method for resampling width. Default is 'nearest_neighbor'.
    curvature_smoothing : bool, optional
        Whether to apply additional smoothing to curvature. Default is True.
    
    Returns
    -------
    x_smooth : numpy.ndarray
        Smoothed x-coordinates.
    y_smooth : numpy.ndarray
        Smoothed y-coordinates.
    s_smooth : numpy.ndarray
        Along-channel distance for smoothed centerline.
    width_smooth : numpy.ndarray
        Channel width resampled to smoothed centerline.
    curvature : numpy.ndarray
        Curvature values (optionally smoothed).
    quality_metrics : dict
        Quality assessment metrics for the resampling.
    """
    
    # Extract centerline coordinates and widths
    x = []
    y = []
    w = []
    for s, e, d in river.main_path:
        key1 = list(river._D_primal[s][e][d]['half_widths'].keys())[0]
        key2 = list(river._D_primal[s][e][d]['half_widths'].keys())[1]
        w1 = river._D_primal[s][e][d]['half_widths'][key1]
        w2 = river._D_primal[s][e][d]['half_widths'][key2]
        x1 = river._D_primal[s][e][d]['geometry'].xy[0]
        y1 = river._D_primal[s][e][d]['geometry'].xy[1]
        x += list(x1)
        y += list(y1)
        w += list(np.array(w1) + np.array(w2))
    
    # Convert to numpy arrays
    x, y, w = np.array(x), np.array(y), np.array(w)
    
    # Get smoothed centerline and curvature
    x_smooth, y_smooth, curvature = resample_and_smooth(x, y, delta_s, smoothing_factor, 
                                                       compute_curvature=True)
    
    # Apply additional curvature smoothing if requested
    if curvature_smoothing:
        curvature = medfilt(savgol_filter(curvature, savgol_factor, 3), kernel_size=5)
    
    # Compute along-channel distance for smoothed centerline
    s_smooth = compute_s_distance(x_smooth, y_smooth)
    
    # Resample width using improved method
    width_smooth, match_distances = resample_channel_width_to_centerline(
        x, y, w, x_smooth, y_smooth, method=width_method)
    
    # Quality assessment
    quality_metrics = {
        'mean_match_distance': np.mean(match_distances),
        'max_match_distance': np.max(match_distances),
        'n_points_original': len(x),
        'n_points_smooth': len(x_smooth),
        'compression_ratio': len(x_smooth) / len(x),
        'invalid_width_points': np.sum(np.isnan(width_smooth)) if np.any(np.isnan(width_smooth)) else 0
    }
    
    return x_smooth, y_smooth, s_smooth, width_smooth, curvature, quality_metrics


def compute_migration_distances(x1, y1, x2, y2, p, q):
    """
    Compute signed migration distances between corresponding points on two centerlines
    without creating plots or verbose output.
    
    Parameters
    ----------
    x1, y1 : array_like
        Coordinates of the first centerline.
    x2, y2 : array_like
        Coordinates of the second centerline.
    p, q : array_like
        DTW correlation indices. p[i] corresponds to q[i], meaning point p[i] 
        on centerline 1 corresponds to point q[i] on centerline 2.
    
    Returns
    -------
    distances : numpy.ndarray
        Array of signed distances with same length as x1. Each value represents
        the average lateral migration distance for that x1 point. Positive values
        indicate leftward migration, negative values indicate rightward migration.
        NaN values indicate x1 points with no DTW correspondences.
    valid_mask : numpy.ndarray
        Boolean array indicating which x1 points have valid distance values.
    
    Examples
    --------
    >>> # Get DTW correlation
    >>> p, q, cost = correlate_curves(x1, x2, y1, y2)
    >>> # Compute migration distances
    >>> distances, valid_mask = compute_migration_distances(x1, y1, x2, y2, p, q)
    >>> # Use only valid distances
    >>> valid_distances = distances[valid_mask]
    >>> valid_x1 = x1[valid_mask]
    """
    
    # Convert inputs to numpy arrays
    x1, y1 = np.array(x1), np.array(y1)
    x2, y2 = np.array(x2), np.array(y2)
    p, q = np.array(p), np.array(q)
    
    # Create arrays to store distances for each x1 point
    distances_by_x1_point = [[] for _ in range(len(x1))]
    
    for i in range(len(p)):
        # Get corresponding point indices
        p_idx = p[i]
        q_idx = q[i]
        
        # Check bounds
        if p_idx < len(x1) and q_idx < len(x2):
            # Get coordinates of corresponding points
            x1_point, y1_point = x1[p_idx], y1[p_idx]
            x2_point, y2_point = x2[q_idx], y2[q_idx]
            
            # Get tangent vector at current point (downstream direction)
            if p_idx == 0:
                # Use forward difference for first point
                if len(x1) > 1:
                    tx = x1[p_idx + 1] - x1[p_idx]
                    ty = y1[p_idx + 1] - y1[p_idx]
                else:
                    tx, ty = 1.0, 0.0  # fallback
            elif p_idx == len(x1) - 1:
                # Use backward difference for last point
                tx = x1[p_idx] - x1[p_idx - 1]
                ty = y1[p_idx] - y1[p_idx - 1]
            else:
                # Use central difference for interior points
                tx = x1[p_idx + 1] - x1[p_idx - 1]
                ty = y1[p_idx + 1] - y1[p_idx - 1]
            
            # Normalize tangent vector
            t_mag = np.sqrt(tx**2 + ty**2)
            if t_mag > 0:
                tx /= t_mag
                ty /= t_mag
            else:
                tx, ty = 1.0, 0.0  # fallback for degenerate case
            
            # Compute normal vector (perpendicular to tangent, pointing left)
            # For a tangent vector (tx, ty), the left normal is (-ty, tx)
            nx = -ty
            ny = tx
            
            # Vector from centerline 1 point to centerline 2 point
            dx = x2_point - x1_point
            dy = y2_point - y1_point
            
            # Compute signed distance using dot product with normal vector
            # Positive when point is to the left of centerline 1 (looking downstream)
            signed_distance = dx * nx + dy * ny
            
            # Add to the list for this x1 point
            distances_by_x1_point[p_idx].append(signed_distance)
    
    # Average distances for each x1 point (NaN if no correspondences)
    distances = np.full(len(x1), np.nan)
    
    for i in range(len(x1)):
        if len(distances_by_x1_point[i]) > 0:
            distances[i] = np.mean(distances_by_x1_point[i])
    
    # Create mask for valid (non-NaN) distances
    valid_mask = ~np.isnan(distances)
    
    return distances, valid_mask


def analyze_river_pairs_filtered(rivers, delta_s=100, smoothing_factor=1e6, 
                                width_method='nearest_neighbor', savgol_factor=21,
                                min_width_m=280, allowed_months=[5,6,7,8], 
                                min_time_gap_days=365, max_time_gap_years=5):
    """
    Analyze river migration using DTW with filtering criteria.
    
    This function performs DTW analysis between river pairs with specific filtering:
    - Only pairs with time gap ≥ min_time_gap_days (default: 365 days)
    - Only rivers from specified months (default: May-August)
    - Only rivers with mean width above threshold (default: 280m)
    - Only pairs with time gap ≤ max_time_gap_years (default: 5 years)
    
    Parameters
    ----------
    rivers : list
        List of River objects with acquisition_date attribute.
    delta_s : float, optional
        Resampling distance. Default is 100.
    smoothing_factor : float, optional
        Smoothing factor for splines. Default is 1e6.
    width_method : str, optional
        Width resampling method. Default is 'nearest_neighbor'.
    savgol_factor : int, optional
        Savitzky-Golay filter window size. Default is 21.
    min_width_m : float, optional
        Minimum mean width in meters. Default is 280.
    allowed_months : list, optional
        List of allowed months (1-12). Default is [5,6,7,8] (May-August).
    min_time_gap_days : int, optional
        Minimum time gap between pairs in days. Default is 365 (1 year).
    max_time_gap_years : float, optional
        Maximum time gap between pairs in years. Default is 5.
    
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'lags': List of lag arrays for each valid pair
        - 'costs': List of DTW costs for each valid pair
        - 'time_gaps': List of time gaps in days for each valid pair
        - 'pair_info': List of dictionaries with pair metadata
        - 'curvatures': List of curvature arrays (from first river) for each valid pair
        - 'migration_distances': List of migration distance arrays for each valid pair
        - 'along_channel_distances': List of along-channel distance arrays (from first river) for each valid pair
        - 'centerline_coords': List of dictionaries with centerline coordinates for each valid pair
          Each dictionary contains 'x1', 'y1', 'x2', 'y2' arrays used in DTW analysis
        - 'filtered_rivers': List of rivers that passed initial filters
        - 'n_total_pairs': Total possible pairs
        - 'n_valid_pairs': Number of pairs that passed all filters
    """
    
    print("Filtering rivers by acquisition criteria...")
    
    # Step 1: Filter individual rivers by month and width
    filtered_rivers = []
    filter_info = []
    
    for i, river in enumerate(rivers):
        try:
            # Check acquisition date month
            date = pd.to_datetime(river.acquisition_date)
            month = date.month
            year = date.year
            
            if month not in allowed_months:
                continue
            
            # Get width and curvature data
            x, y, s, width, curvature, quality = get_width_and_curvature(
                river, delta_s=delta_s, smoothing_factor=smoothing_factor, 
                width_method=width_method, curvature_smoothing=True, 
                savgol_factor=savgol_factor)
            
            # Check mean width criterion (30m pixel size factor)
            mean_width_m = np.mean(width) * 30
            
            if mean_width_m >= min_width_m:
                filtered_rivers.append(river)
                filter_info.append({
                    'original_index': i,
                    'date': date,
                    'year': year,
                    'month': month,
                    'mean_width_m': mean_width_m,
                    'x': x, 'y': y, 's': s, 'width': width, 'curvature': curvature
                })
        
        except Exception as e:
            print(f"Warning: Failed to process river {i}: {e}")
            continue
    
    print(f"Rivers passing filters: {len(filtered_rivers)} out of {len(rivers)}")
    print(f"  Month filter ({allowed_months}): Included rivers from allowed months")
    print(f"  Width filter (≥{min_width_m}m): Included rivers with sufficient width")
    
    # Step 2: Analyze pairs with additional filtering
    lags = []
    costs = []
    time_gaps = []
    pair_info = []
    widths = []
    curvatures = []  # Store curvature of first river for each pair
    migration_distances = []  # Store migration distances for each pair
    along_channel_distances = []  # Store along-channel distance of first river for each pair
    centerline_coords = []  # Store centerline coordinates (x1, y1, x2, y2) for each pair
    
    n_total_pairs = 0
    n_valid_pairs = 0
    
    print("\nAnalyzing river pairs...")
    
    # Create pairs (can be consecutive or all combinations)
    for i in trange(len(filtered_rivers)):
        for j in range(i + 1, len(filtered_rivers)):
            n_total_pairs += 1
            
            river1 = filtered_rivers[i]
            river2 = filtered_rivers[j]
            info1 = filter_info[i]
            info2 = filter_info[j]
            
            # Check time gap criteria
            time_gap_days = (info2['date'] - info1['date']).days
            time_gap_years = abs(time_gap_days) / 365.25
            
            # Check minimum time gap criterion
            if abs(time_gap_days) < min_time_gap_days:
                continue
                
            # Check maximum time gap criterion
            if time_gap_years > max_time_gap_years:
                continue
            
            try:
                # Extract pre-computed data
                x1, y1, width1, curvature1 = info1['x'], info1['y'], info1['width'], info1['curvature']
                x2, y2, width2, curvature2 = info2['x'], info2['y'], info2['width'], info2['curvature']
                s1 = info1['s']
                s2 = info2['s']
                
                # Use pre-computed time gap
                time_gaps.append(time_gap_days)
                
                # DTW correlation between centerlines
                p, q, cost = correlate_curves(x1, x2, y1, y2)
                distances, valid_mask = compute_migration_distances(x1, y1, x2, y2, p, q)
                distances = medfilt(savgol_filter(distances, 11, 3), kernel_size=5)
                
                # Compute normalized migration rates and curvature
                W = 30 * np.mean(width1)  # Mean width in meters
                mr = distances / W  # Normalized migration rate
                curv = -curvature1 * W  # Normalized curvature (note: negative sign)
                
                # Create similarity matrix
                sm = np.zeros((len(s1), len(s1)))
                for k in range(len(s1)):
                    sm[k, :] = (np.abs(mr - curv[k]))**0.07
                
                # DTW on similarity matrix
                D, wp = dtw(C=sm)
                costs.append(D[-1, -1])
                
                # Extract lag information
                p1 = wp[:, 0]  # correlation indices for first curve
                q1 = wp[:, 1]  # correlation indices for second curve
                p1 = np.array(p1)
                q1 = np.array(q1)
                
                pair_lags = []
                for k in range(len(p1)):
                    pair_lags.append(s1[p1[k]] - s1[q1[k]])
                lags.append(pair_lags)
                
                # Store curvature and migration data
                widths.append(width1.copy())
                curvatures.append(curvature1.copy())  # Store curvature of first river
                migration_distances.append(distances.copy())  # Store migration distances
                along_channel_distances.append(s1.copy())  # Store along-channel distance of first river
                
                # Store centerline coordinates used in DTW analysis
                centerline_coords.append({
                    'x1': x1.copy(),
                    'y1': y1.copy(), 
                    'x2': x2.copy(),
                    'y2': y2.copy()
                })
                
                # Store pair metadata
                pair_info.append({
                    'river1_index': info1['original_index'],
                    'river2_index': info2['original_index'],
                    'date1': info1['date'],
                    'date2': info2['date'],
                    'year1': info1['year'],
                    'year2': info2['year'],
                    'time_gap_days': time_gap_days,
                    'time_gap_years': time_gap_years,
                    's1': s1,
                    's2': s2,
                    'width1_m': info1['mean_width_m'],
                    'width2_m': info2['mean_width_m'],
                    'dtw_cost': D[-1, -1],
                    'n_correspondences': len(p),
                    'n_valid_distances': np.sum(valid_mask)
                })
                
                n_valid_pairs += 1
                
            except Exception as e:
                print(f"Warning: Failed to analyze pair {i}-{j}: {e}")
                continue
    
    # Summary
    print(f"\nAnalysis Summary:")
    print(f"  Total possible pairs: {n_total_pairs}")
    print(f"  Valid pairs analyzed: {n_valid_pairs}")
    print(f"  Success rate: {n_valid_pairs/n_total_pairs*100:.1f}%")
    
    if n_valid_pairs > 0:
        time_gap_years_list = [abs(gap)/365.25 for gap in time_gaps]
        print(f"  Time gap range: {min(time_gaps):.0f} to {max(time_gaps):.0f} days ({min(time_gap_years_list):.1f} to {max(time_gap_years_list):.1f} years)")
        print(f"  Cost range: {min(costs):.3f} to {max(costs):.3f}")
        print(f"  Filters applied:")
        print(f"    - Min time gap: {min_time_gap_days} days ({min_time_gap_days/365.25:.1f} years)")
        print(f"    - Max time gap: {max_time_gap_years} years")
        print(f"    - Allowed months: {allowed_months}")
        print(f"    - Min width: {min_width_m}m")
    
    return {
        'lags': lags,
        'costs': costs,
        'time_gaps': time_gaps,
        'pair_info': pair_info,
        'widths': widths,
        'curvatures': curvatures,  # Curvature of first river for each pair
        'migration_distances': migration_distances,  # Migration distances for each pair
        'along_channel_distances': along_channel_distances,  # Along-channel distance of first river for each pair
        'centerline_coords': centerline_coords,  # Centerline coordinates (x1, y1, x2, y2) for each pair
        'filtered_rivers': filtered_rivers,
        'filter_info': filter_info,
        'n_total_pairs': n_total_pairs,
        'n_valid_pairs': n_valid_pairs
    }