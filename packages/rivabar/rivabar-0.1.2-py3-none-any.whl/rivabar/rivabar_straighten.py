import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LinearRing, LineString

def resample_and_smooth(x, y, ds, smoothing):
    """
    Resample and smooth a line.
    
    Parameters
    ----------
    x : array_like
        The x-coordinates of the line.
    y : array_like
        The y-coordinates of the line.
    ds : float
        The distance between points after resampling.
    smoothing : float
        The smoothing factor for the spline.
        
    Returns
    -------
    x_new : ndarray
        The x-coordinates of the resampled and smoothed line.
    y_new : ndarray
        The y-coordinates of the resampled and smoothed line.
    """
    # Calculate the total length of the line
    dx = np.diff(x)
    dy = np.diff(y)
    length = np.sum(np.sqrt(dx**2 + dy**2))
    
    # Calculate the number of points for resampling
    n_points = int(length / ds)
    
    # Fit a spline to the line
    tck, u = splprep([x, y], s=smoothing, k=3)
    
    # Resample the line
    u_new = np.linspace(0, 1, n_points)
    x_new, y_new = splev(u_new, tck)
    
    return x_new, y_new

def straighten_channel(xl, yl, xls, yls):
    """
    Straighten a channel centerline while preserving local shapes.
    
    Parameters
    ----------
    xl : array_like
        The x-coordinates of the original sinuous channel.
    yl : array_like
        The y-coordinates of the original sinuous channel.
    xls : array_like
        The x-coordinates of the smoothed centerline.
    yls : array_like
        The y-coordinates of the smoothed centerline.
        
    Returns
    -------
    xl_straight : ndarray
        The x-coordinates of the straightened channel.
    yl_straight : ndarray
        The y-coordinates of the straightened channel.
    """
    xl = np.array(xl)
    yl = np.array(yl)
    xls = np.array(xls)
    yls = np.array(yls)
    
    # Calculate the distances along the smoothed centerline
    dxs = np.diff(xls)
    dys = np.diff(yls)
    ds = np.sqrt(dxs**2 + dys**2)
    s = np.zeros(len(xls))
    s[1:] = np.cumsum(ds)
    
    # Create a straight reference line with the same total length
    xref = np.zeros_like(xls)
    yref = s
    
    # For each point in the original centerline, find the closest point on the smoothed centerline
    xl_straight = np.zeros_like(xl)
    yl_straight = np.zeros_like(yl)
    
    for i in range(len(xl)):
        # Find the closest point on the smoothed centerline
        dist_to_smooth = np.sqrt((xl[i] - xls)**2 + (yl[i] - yls)**2)
        closest_idx = np.argmin(dist_to_smooth)
        
        # If closest point is at the start or end, just use that point
        if closest_idx == 0:
            tangent_angle = np.arctan2(dys[0], dxs[0])
            normal_angle = tangent_angle + np.pi/2
            
            # Vector from smoothed centerline to original point
            dx = xl[i] - xls[0]
            dy = yl[i] - yls[0]
            
            # Project onto normal direction to get signed distance
            normal_dist = dx * np.cos(normal_angle) + dy * np.sin(normal_angle)
            
            # Map to the straight reference line
            xl_straight[i] = normal_dist
            yl_straight[i] = 0
            
        elif closest_idx == len(xls) - 1:
            tangent_angle = np.arctan2(dys[-1], dxs[-1])
            normal_angle = tangent_angle + np.pi/2
            
            # Vector from smoothed centerline to original point
            dx = xl[i] - xls[-1]
            dy = yl[i] - yls[-1]
            
            # Project onto normal direction to get signed distance
            normal_dist = dx * np.cos(normal_angle) + dy * np.sin(normal_angle)
            
            # Map to the straight reference line
            xl_straight[i] = normal_dist
            yl_straight[i] = s[-1]
            
        else:
            # For interior points, interpolate between the two nearest segments
            tangent_angle = np.arctan2(dys[closest_idx], dxs[closest_idx])
            normal_angle = tangent_angle + np.pi/2
            
            # Vector from smoothed centerline to original point
            dx = xl[i] - xls[closest_idx]
            dy = yl[i] - yls[closest_idx]
            
            # Project onto normal direction to get signed distance
            normal_dist = dx * np.cos(normal_angle) + dy * np.sin(normal_angle)
            
            # Map to the straight reference line
            xl_straight[i] = normal_dist
            yl_straight[i] = s[closest_idx]
            
    return xl_straight, yl_straight

def straighten_polygon(polygon, xls, yls):
    """
    Straighten a polygon along a centerline.
    
    Parameters
    ----------
    polygon : shapely.geometry.Polygon
        The polygon to straighten.
    xls : array_like
        The x-coordinates of the smoothed centerline.
    yls : array_like
        The y-coordinates of the smoothed centerline.
        
    Returns
    -------
    straight_polygon : shapely.geometry.Polygon
        The straightened polygon.
    """
    # Extract polygon exterior coordinates
    xl_exterior = np.array(polygon.exterior.xy[0])
    yl_exterior = np.array(polygon.exterior.xy[1])
    
    # Straighten the exterior coordinates
    xl_straight, yl_straight = straighten_channel(xl_exterior, yl_exterior, xls, yls)
    
    # Create a new exterior ring
    exterior_straight = LinearRing(np.column_stack([xl_straight, yl_straight]))
    
    # Straighten each interior ring (hole) if any
    interior_rings_straight = []
    for interior in polygon.interiors:
        xl_interior = np.array(interior.xy[0])
        yl_interior = np.array(interior.xy[1])
        
        # Straighten the interior coordinates
        xl_interior_straight, yl_interior_straight = straighten_channel(xl_interior, yl_interior, xls, yls)
        
        # Create a new interior ring
        interior_straight = LinearRing(np.column_stack([xl_interior_straight, yl_interior_straight]))
        interior_rings_straight.append(interior_straight)
    
    # Create the straightened polygon
    straight_polygon = Polygon(exterior_straight, interior_rings_straight)
    
    return straight_polygon

def plot_straightening_comparison(original_polygon, straightened_polygon):
    """
    Plot the original sinuous polygon and the straightened polygon for comparison.
    
    Parameters
    ----------
    original_polygon : shapely.geometry.Polygon
        The original sinuous polygon.
    straightened_polygon : shapely.geometry.Polygon
        The straightened polygon.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plots.
    (ax1, ax2) : tuple of matplotlib.axes.Axes
        The subplots containing the original and straightened polygons.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Original polygon
    x_orig, y_orig = original_polygon.exterior.xy
    ax1.plot(x_orig, y_orig, 'k-', lw=1)
    
    # Plot interior rings (holes) if any
    for interior in original_polygon.interiors:
        x_int, y_int = interior.xy
        ax1.plot(x_int, y_int, 'k-', lw=1)
    
    ax1.set_aspect('equal')
    ax1.set_title('Original Sinuous Polygon')
    
    # Straightened polygon
    x_straight, y_straight = straightened_polygon.exterior.xy
    ax2.plot(x_straight, y_straight, 'k-', lw=1)
    
    # Plot interior rings (holes) if any
    for interior in straightened_polygon.interiors:
        x_int, y_int = interior.xy
        ax2.plot(x_int, y_int, 'k-', lw=1)
    
    ax2.set_aspect('equal')
    ax2.set_title('Straightened Polygon')
    
    plt.tight_layout()
    return fig, (ax1, ax2) 