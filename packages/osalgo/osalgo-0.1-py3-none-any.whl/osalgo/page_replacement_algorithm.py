def _format_page_table(title, results):
    """
    Helper function to format the simulation results into a readable string table.
    
    Args:
        title (str): The title for the simulation (e.g., "FIFO Simulation").
        results (dict): The dictionary containing simulation output.
    """
    pages = results["pages"]
    num_frames = results["num_frames"]
    frames_history = results["frames_history"]
    fault_hit_history = results["fault_hit_history"]
    
    # Calculate cell width based on the longest page number or a minimum of 3
    cell_width = max(max(len(str(p)) for p in pages), 3) + 1
    
    # 1. Header Row (Page Reference String)
    header = "Page No. | " + " | ".join(f"{p:^{cell_width-1}}" for p in pages) + " |"
    separator = "=" * len(header)
    table_lines = [separator, title, separator, "\n--- Simulation Table ---"]

    table_lines.append(header)
    table_lines.append("-" * len(header))

    # 2. Frame Rows
    for i in range(num_frames):
        row = f"Frame {i+1} |"
        for j in range(len(pages)):
            page_in_frame = frames_history[j][i]
            # Display space for empty frames (-1)
            display_value = str(page_in_frame) if page_in_frame != -1 else ' '
            row += f" {display_value:^{cell_width-1}} |"
        table_lines.append(row)
        
    table_lines.append("-" * len(header))

    # 3. Fault/Hit Row
    fault_hit_row = f"F/H      | " + " | ".join(f"{fh:^{cell_width-1}}" for fh in fault_hit_history) + " |"
    table_lines.append(fault_hit_row)
    table_lines.append(separator)
    
    # 4. Summary Output
    summary = (
        f"\nTotal Pages: {len(pages)}\n"
        f"Number of Frames: {num_frames}\n"
        f"Number of Page Faults: {results['page_faults']}\n"
        f"Number of Page Hits: {results['page_hits']}"
    )
    
    print("\n".join(table_lines) + summary)


# ==============================================================================
# 1. FIFO (First-In, First-Out) Page Replacement Algorithm
# ==============================================================================

def fifo_page_replacement(page_reference_string, num_frames):
    """
    Simulates the FIFO page replacement algorithm and prints the results table.
    """
    pages = page_reference_string
    frames_history = []
    frames = [-1] * num_frames
    fault_hit_history = []
    page_faults = 0
    page_hits = 0
    
    # FIFO queue tracks the order in which pages entered the frames
    fifo_queue = []
    
    for page in pages:
        is_hit = False
        
        if page in frames:
            page_hits += 1
            fault_hit_history.append('H')
            is_hit = True
        else:
            page_faults += 1
            fault_hit_history.append('F')
            
            # Case 1: Empty slot available
            if -1 in frames:
                try:
                    empty_index = frames.index(-1)
                    frames[empty_index] = page
                    # Add new page to the back of the queue
                    fifo_queue.append(page)
                except ValueError:
                    pass
            
            # Case 2: Frames are full, replace the page at the front of the queue
            else:
                # Page to replace is the oldest one (FIFO)
                page_to_replace = fifo_queue.pop(0)
                
                try:
                    replace_index = frames.index(page_to_replace)
                    frames[replace_index] = page
                    # Add the new page to the back of the queue
                    fifo_queue.append(page)
                except ValueError:
                    # This should not happen if logic is correct, but safe to handle
                    pass

        # Record the state of the frames after processing the current page reference
        frames_history.append(list(frames))

    results = {
        "pages": pages,
        "num_frames": num_frames,
        "frames_history": frames_history,
        "fault_hit_history": fault_hit_history,
        "page_faults": page_faults,
        "page_hits": page_hits
    }
    
    _format_page_table("FIFO (First-In, First-Out) Page Replacement", results)


# ==============================================================================
# 2. LRU (Least Recently Used) Page Replacement Algorithm
# ==============================================================================

def lru_page_replacement(page_reference_string, num_frames):
    """
    Simulates the LRU page replacement algorithm and prints the results table.
    """
    pages = page_reference_string
    frames_history = []
    frames = [-1] * num_frames
    fault_hit_history = []
    page_faults = 0
    page_hits = 0
    
    # LRU list tracks usage order: start is LRU, end is MRU (Most Recently Used)
    lru_list = []

    for page in pages:
        
        if page in frames:
            page_hits += 1
            fault_hit_history.append('H')
            
            # Hit: Move the hit page to the MRU position (end of the list)
            if page in lru_list:
                lru_list.remove(page)
            lru_list.append(page)
            
        else:
            page_faults += 1
            fault_hit_history.append('F')
            
            # Case 1: Empty slot available
            if -1 in frames:
                try:
                    empty_index = frames.index(-1)
                    frames[empty_index] = page
                except ValueError:
                    pass # Should not happen

            # Case 2: Frames are full, replace the LRU page
            else:
                # Page to replace is the LRU page (first element in the list)
                page_to_replace = lru_list.pop(0)
                
                try:
                    replace_index = frames.index(page_to_replace)
                    frames[replace_index] = page
                except ValueError:
                    pass # Should not happen

            # Add the new page to the MRU position
            lru_list.append(page)
            
        # Record the state of the frames
        frames_history.append(list(frames))

    results = {
        "pages": pages,
        "num_frames": num_frames,
        "frames_history": frames_history,
        "fault_hit_history": fault_hit_history,
        "page_faults": page_faults,
        "page_hits": page_hits
    }
    
    _format_page_table("LRU (Least Recently Used) Page Replacement", results)


# if __name__ == "__main__":
#     # --- Example Usage ---
    
#     # Common reference string for demonstration
#     example_pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
#     example_frames = 3
    
#     print("==================================================================")
#     print("Demonstration of Page Replacement Algorithms Module")
#     print("Reference String:", example_pages)
#     print("Number of Frames:", example_frames)
#     print("==================================================================")

#     # 1. Run FIFO
#     fifo_page_replacement(example_pages, example_frames)
    
#     print("\n\n")

#     # 2. Run LRU
#     lru_page_replacement(example_pages, example_frames)
