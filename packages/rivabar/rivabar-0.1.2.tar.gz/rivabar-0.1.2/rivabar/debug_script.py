#!/usr/bin/env python3
"""
Debug script for rivabar development
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rivabar.core as rb

def debug_extract_centerline():
    """Debug the extract_centerline function with Branco River example"""
    
    # Branco River example parameters
    fname = 'LC08_L2SP_232060_20140219_20200911_02_T1_SR'
    dirname = 'data/Branco/'
    start_x = 676984.422077922
    start_y = 100153.4025974026
    end_x = 627887.5519480519
    end_y = -93222.0
    file_type = 'multiple_tifs'
    
    # Set breakpoint here to debug step by step
    print(f"Starting centerline extraction for {fname}")
    
    try:
        result = rb.extract_centerline(
            fname=fname,
            dirname=dirname,
            start_x=start_x,
            start_y=start_y,
            end_x=end_x,
            end_y=end_y,
            file_type=file_type,
            mndwi_threshold=0.01,
            ch_belt_smooth_factor=1e8,
            ch_belt_half_width=2000,
            remove_smaller_components=True,
            plot_D_primal=True
        )
        
        D_primal, G_rook, G_primal, mndwi, dataset, left_utm_x, right_utm_x, lower_utm_y, upper_utm_y, xs, ys = result
        
        print(f"Successfully extracted centerline!")
        print(f"D_primal nodes: {len(D_primal.nodes())}")
        print(f"G_rook nodes: {len(G_rook.nodes())}")
        print(f"G_primal nodes: {len(G_primal.nodes())}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extract_centerline()