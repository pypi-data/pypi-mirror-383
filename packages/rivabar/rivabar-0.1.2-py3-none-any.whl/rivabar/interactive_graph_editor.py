import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from tqdm import tqdm

def plot_graph_interactive(D_primal, plot_colored_line_func, ax=None, figsize=(15, 10)):
    """
    Interactive plot of D_primal graph where you can click on edges to flip their directions.
    
    Parameters:
    -----------
    D_primal : networkx.MultiDiGraph
        The directed multigraph to plot
    plot_colored_line_func : function
        The plot_colored_line function from rivabar (pass rivabar.plot_colored_line)
    ax : matplotlib axis, optional
        Existing axis to plot on
    figsize : tuple
        Figure size if creating new figure
        
    Returns:
    --------
    fig, ax : matplotlib figure and axis
    edge_data : list
        List of edge information for reference
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()
    
    # Store edge information for click detection
    edge_data = []
    
    def plot_edges():
        """Plot all edges and store their data"""
        ax.clear()
        edge_data.clear()
        
        # Plot edges
        for s, e, d in tqdm(D_primal.edges):
            edge_geom = D_primal[s][e][d]['geometry']
            x = np.array(edge_geom.xy[0])
            y = np.array(edge_geom.xy[1])
            
            # Store edge data for click detection
            edge_data.append({
                'start': s,
                'end': e,
                'key': d,
                'geometry': edge_geom,
                'x': x,
                'y': y
            })
            
            # Plot the edge using the provided function
            plot_colored_line_func(x, y, linewidth=2, cmap='magma', ax=ax)
        
        # Plot source and sink nodes
        sources = [node for node in D_primal.nodes() if D_primal.in_degree(node) == 0]
        sinks = [node for node in D_primal.nodes() if D_primal.out_degree(node) == 0]
        
        for i, node in enumerate(sources):
            x = D_primal.nodes()[node]['geometry'].xy[0][0]
            y = D_primal.nodes()[node]['geometry'].xy[1][0]
            ax.plot(x, y, 'o', color='blue', markersize=8, zorder=10, 
                   label='Source' if i == 0 else "")
        
        for i, node in enumerate(sinks):
            x = D_primal.nodes()[node]['geometry'].xy[0][0]
            y = D_primal.nodes()[node]['geometry'].xy[1][0]
            ax.plot(x, y, 'o', color='black', markersize=8, zorder=10, 
                   label='Sink' if i == 0 else "")
        
        ax.set_title('Interactive D_primal Graph - Click on edges to flip directions')
        if sources or sinks:
            ax.legend()
        ax.grid(True, alpha=0.3)
        fig.canvas.draw()
    
    def find_closest_edge(click_x, click_y):
        """Find the edge closest to the click coordinates"""
        min_distance = float('inf')
        closest_edge = None
        
        for edge in edge_data:
            # Calculate minimum distance from click point to edge line segments
            x_coords = edge['x']
            y_coords = edge['y']
            
            for i in range(len(x_coords) - 1):
                # Line segment from (x1,y1) to (x2,y2)
                x1, y1 = x_coords[i], y_coords[i]
                x2, y2 = x_coords[i + 1], y_coords[i + 1]
                
                # Calculate distance from point to line segment
                A = click_x - x1
                B = click_y - y1
                C = x2 - x1
                D = y2 - y1
                
                dot = A * C + B * D
                len_sq = C * C + D * D
                
                if len_sq == 0:
                    # Point case
                    distance = np.sqrt(A * A + B * B)
                else:
                    param = dot / len_sq
                    
                    if param < 0:
                        xx, yy = x1, y1
                    elif param > 1:
                        xx, yy = x2, y2
                    else:
                        xx = x1 + param * C
                        yy = y1 + param * D
                    
                    dx = click_x - xx
                    dy = click_y - yy
                    distance = np.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_edge = edge
        
        return closest_edge, min_distance
    
    def flip_edge_direction(edge_info):
        """Flip the direction of an edge in the graph"""
        start = edge_info['start']
        end = edge_info['end']
        key = edge_info['key']
        
        # Get edge attributes
        edge_attrs = D_primal[start][end][key].copy()
        
        # Remove the original edge
        D_primal.remove_edge(start, end, key)
        
        # Add the edge in reverse direction
        # Reverse the geometry coordinates
        geom = edge_attrs['geometry']
        reversed_coords = list(zip(geom.xy[0][::-1], geom.xy[1][::-1]))
        
        # Create new geometry with reversed coordinates
        edge_attrs['geometry'] = LineString(reversed_coords)
        
        # Add the reversed edge
        D_primal.add_edge(end, start, **edge_attrs)
        
        print(f"Flipped edge direction: ({start}, {end}) -> ({end}, {start})")
    
    def on_click(event):
        """Handle mouse click events"""
        if event.inaxes != ax:
            return
        
        if event.button == 1:  # Left mouse button
            click_x, click_y = event.xdata, event.ydata
            
            if click_x is None or click_y is None:
                return
            
            # Find closest edge
            closest_edge, distance = find_closest_edge(click_x, click_y)
            
            if closest_edge is not None:
                # Set a reasonable threshold for clicks (you can adjust this)
                # Convert to data coordinates - this is a rough threshold
                x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
                y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
                threshold = max(x_range, y_range) * 0.02  # 2% of the range
                
                if distance < threshold:
                    # Flip the edge direction
                    flip_edge_direction(closest_edge)
                    
                    # Replot the graph
                    plot_edges()
                    
                    print(f"Edge flipped! Distance to click: {distance:.2f}")
                else:
                    print(f"Click too far from any edge. Distance: {distance:.2f}, threshold: {threshold:.2f}")
    
    # Initial plot
    plot_edges()
    
    # Connect the click event
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    print("Interactive plot ready!")
    print("Instructions:")
    print("- Left-click on an edge to flip its direction")
    print("- Blue circles = source nodes (in-degree = 0)")
    print("- Black circles = sink nodes (out-degree = 0)")
    print("- The graph will update automatically after each flip")
    
    return fig, ax, edge_data

def plot_graph_w_colors_interactive(D_primal, plot_colored_line_func, ax=None):
    """
    Wrapper function that mimics the original plot_graph_w_colors but with interactivity
    """
    return plot_graph_interactive(D_primal, plot_colored_line_func, ax) 