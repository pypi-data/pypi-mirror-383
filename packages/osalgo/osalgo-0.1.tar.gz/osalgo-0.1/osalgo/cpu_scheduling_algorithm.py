# --- Helper Function for Formatting Output ---

def _print_metrics_table(title, processes, avg_tat, avg_wt):
    """Prints the calculated metrics in a well-formatted table."""
    
    # Calculate total length needed for the table
    W_P = 15  # Process Name
    W_AT = 15 # Arrival Time
    W_BT = 15 # Burst Time
    W_CT = 20 # Completion Time
    W_TAT = 20 # Turnaround Time
    W_WT = 20 # Waiting Time
    W_PRI = 10 # Priority (if present)
    
    has_priority = any('priority' in p for p in processes)
    
    # Build the header string
    header_format = f"{{:<{W_P}}}{{:>{W_AT}}}{{:>{W_BT}}}"
    header_labels = ["Process Name", "Arrival Time", "Burst Time"]
    
    if has_priority:
        header_format += f"{{:>{W_PRI}}}"
        header_labels.append("Priority")

    header_format += f"{{:>{W_CT}}}{{:>{W_TAT}}}{{:>{W_WT}}}"
    header_labels.extend(["Completion Time", "Turnaround Time", "Waiting Time"])
    
    header = header_format.format(*header_labels)
    separator = "=" * len(header)
    
    print("\n" + "=" * len(separator))
    print(title)
    print(separator)

    print("\n--- Process Metrics Table ---")
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    # Data Rows
    for p in processes:
        row_values = [p['name'], p['at'], p['bt']]
        if has_priority:
            row_values.append(p['priority'])

        # Ensure that CT, TAT, and WT are calculated before trying to print
        if 'ct' in p:
            row_values.extend([p['ct'], p['tat'], p['wt']])
        else:
            # Handle cases where a process might not have run (shouldn't happen here)
            row_values.extend(['N/A', 'N/A', 'N/A'])

        row = header_format.format(*row_values)
        print(row)
        
    print("-" * len(header))

    # Summary
    print(f"\nAverage Turnaround Time: {avg_tat:.2f} ms")
    print(f"Average Waiting Time:    {avg_wt:.2f} ms")


# ==============================================================================
# 1. First-Come, First-Served (FCFS) - Non-Preemptive
# ==============================================================================

def fcfs_scheduling(process_list, arrival_time_list, burst_time_list):
    """Calculates metrics for FCFS scheduling."""
    if not (len(process_list) == len(arrival_time_list) == len(burst_time_list)):
        print("Error: All input lists must have the same length.")
        return

    processes = []
    for i, (p, at, bt) in enumerate(zip(process_list, arrival_time_list, burst_time_list)):
        processes.append({'name': p, 'at': at, 'bt': bt, 'original_index': i})

    # FCFS: Sort strictly by Arrival Time (AT)
    processes.sort(key=lambda x: x['at'])
    
    n = len(processes)
    current_time = 0
    total_tat = 0
    total_wt = 0
    
    # List to store the final results in the original process order
    final_results = [None] * n

    for process in processes:
        # Start Time: Wait until arrival (process['at']) AND CPU is free (current_time)
        start_time = max(current_time, process['at'])
        
        completion_time = start_time + process['bt']
        turnaround_time = completion_time - process['at']
        waiting_time = turnaround_time - process['bt']

        # Update process dictionary with results
        process['ct'] = completion_time
        process['tat'] = turnaround_time
        process['wt'] = waiting_time
        
        # Update counters and time
        current_time = completion_time
        total_tat += turnaround_time
        total_wt += waiting_time
        
        # Store result
        final_results[process['original_index']] = process

    avg_tat = total_tat / n if n > 0 else 0
    avg_wt = total_wt / n if n > 0 else 0
    _print_metrics_table("First-Come, First-Served (FCFS)", final_results, avg_tat, avg_wt)


# ==============================================================================
# 2. Shortest Job First (SJF) - Non-Preemptive
# ==============================================================================

def sjf_scheduling_non_preemptive(process_list, arrival_time_list, burst_time_list):
    """Calculates metrics for Non-Preemptive SJF scheduling."""
    if not (len(process_list) == len(arrival_time_list) == len(burst_time_list)):
        print("Error: All input lists must have the same length.")
        return

    processes = []
    for i, (p, at, bt) in enumerate(zip(process_list, arrival_time_list, burst_time_list)):
        processes.append({'name': p, 'at': at, 'bt': bt, 'original_index': i})

    # Sort primarily by Arrival Time, secondarily by Burst Time for initial tie-breaking
    processes.sort(key=lambda x: (x['at'], x['bt']))
    
    n = len(processes)
    completed_count = 0
    current_time = 0
    total_tat = 0
    total_wt = 0
    
    final_results = [None] * n

    while completed_count < n:
        # Ready queue: Processes arrived by current_time and not yet completed
        ready_queue = [p for p in processes if p['at'] <= current_time and 'ct' not in p]
        
        if ready_queue:
            # Select the job with the minimum Burst Time (SJF)
            # Sort by Burst Time (BT), then Arrival Time (AT) for tie-breaking
            ready_queue.sort(key=lambda x: (x['bt'], x['at']))
            
            selected_process = ready_queue[0]
            
            # Find the index of the selected process in the main 'processes' list
            selected_index = processes.index(selected_process)
            
            # Non-Preemptive: runs to completion
            burst_time = selected_process['bt']
            
            completion_time = current_time + burst_time
            turnaround_time = completion_time - selected_process['at']
            waiting_time = turnaround_time - burst_time

            # Update process dictionary with results
            selected_process['ct'] = completion_time
            selected_process['tat'] = turnaround_time
            selected_process['wt'] = waiting_time
            
            # Update counters
            current_time = completion_time
            total_tat += turnaround_time
            total_wt += waiting_time
            completed_count += 1
            
            # Store result and remove from main list to avoid re-selection
            final_results[selected_process['original_index']] = selected_process
            del processes[selected_index]
        
        else:
            # CPU is idle. Advance time to the arrival time of the next process.
            next_arrival = float('inf')
            found_next = False
            for p in processes:
                if p['at'] > current_time and 'ct' not in p:
                    next_arrival = min(next_arrival, p['at'])
                    found_next = True
            
            if found_next:
                current_time = next_arrival
            else:
                break

    avg_tat = total_tat / n if n > 0 else 0
    avg_wt = total_wt / n if n > 0 else 0
    _print_metrics_table("Shortest Job First (SJF) - Non-Preemptive", final_results, avg_tat, avg_wt)


# ==============================================================================
# 3. Shortest Remaining Time Next (SRTN) - Preemptive
# ==============================================================================

def srtn_scheduling_preemptive(process_list, arrival_time_list, burst_time_list):
    """Calculates metrics for Preemptive SRTN scheduling."""
    if not (len(process_list) == len(arrival_time_list) == len(burst_time_list)):
        print("Error: All input lists must have the same length.")
        return

    # 1. Initialize Processes and Data
    processes = []
    for i, (p, at, bt) in enumerate(zip(process_list, arrival_time_list, burst_time_list)):
        processes.append({
            'name': p, 
            'at': at, 
            'bt': bt, 
            'rem_bt': bt, # Remaining Burst Time (key for SRTN)
            'original_index': i
        })
    
    n = len(processes)
    completed_count = 0
    current_time = 0
    
    # Metrics
    total_tat = 0
    total_wt = 0
    
    final_results = [None] * n

    while completed_count < n:
        # 2. Identify the ready queue (arrived processes with remaining work)
        ready_queue = [p for p in processes if p['at'] <= current_time and p['rem_bt'] > 0]

        if not ready_queue:
            # CPU is idle. Advance time to the arrival time of the next unarrived process.
            next_arrival = float('inf')
            found_next = False
            for p in processes:
                if p['at'] > current_time and p['rem_bt'] > 0 and p['at'] < next_arrival:
                    next_arrival = p['at']
                    found_next = True
            
            if found_next:
                current_time = next_arrival
                continue
            else:
                break

        # 3. Select the Shortest Remaining Time (SRTN) process
        # Sort by Remaining Burst Time (rem_bt), then Arrival Time (at) for tie-breaking
        ready_queue.sort(key=lambda x: (x['rem_bt'], x['at']))
        selected_process = ready_queue[0]

        # 4. Execution (Run for 1 time unit)
        selected_process['rem_bt'] -= 1
        current_time += 1
        
        # 5. Check for Completion
        if selected_process['rem_bt'] == 0:
            
            completion_time = current_time
            turnaround_time = completion_time - selected_process['at']
            waiting_time = turnaround_time - selected_process['bt'] # Use original BT

            # Update process dictionary with results
            selected_process['ct'] = completion_time
            selected_process['tat'] = turnaround_time
            selected_process['wt'] = waiting_time
            
            # Update counters
            total_tat += turnaround_time
            total_wt += waiting_time
            completed_count += 1
            
            # Store result
            final_results[selected_process['original_index']] = selected_process

    # 6. Final Calculation and Display
    avg_tat = total_tat / n if n > 0 else 0
    avg_wt = total_wt / n if n > 0 else 0
    
    # The final_results list may contain None if any process failed to complete,
    # but given the loop logic, it should contain all completed processes.
    
    # We need to sort the final results back by original index for proper table display
    final_results.sort(key=lambda x: x['original_index'])
    _print_metrics_table("Shortest Remaining Time Next (SRTN) - Preemptive", final_results, avg_tat, avg_wt)


# ==============================================================================
# 4. Priority Scheduling - Non-Preemptive (Lower number = Higher Priority)
# ==============================================================================

def priority_scheduling_non_preemptive(process_list, arrival_time_list, burst_time_list, priority_list):
    """Calculates metrics for Non-Preemptive Priority scheduling."""
    if not (len(process_list) == len(arrival_time_list) == len(burst_time_list) == len(priority_list)):
        print("Error: All input lists must have the same length.")
        return

    processes = []
    for i, (p, at, bt, pri) in enumerate(zip(process_list, arrival_time_list, burst_time_list, priority_list)):
        processes.append({'name': p, 'at': at, 'bt': bt, 'priority': pri, 'original_index': i})

    # Sort primarily by Arrival Time, secondarily by Priority for initial tie-breaking
    processes.sort(key=lambda x: (x['at'], x['priority']))
    
    n = len(processes)
    completed_count = 0
    current_time = 0
    total_tat = 0
    total_wt = 0
    
    final_results = [None] * n

    while completed_count < n:
        # Ready queue: Processes arrived by current_time and not yet completed
        ready_queue = [p for p in processes if p['at'] <= current_time and 'ct' not in p]
        
        if ready_queue:
            # Select the job with the highest Priority (minimum priority number)
            # Sort by Priority (priority), then Arrival Time (at) for tie-breaking
            ready_queue.sort(key=lambda x: (x['priority'], x['at']))
            
            selected_process = ready_queue[0]
            
            # Find the index of the selected process in the main 'processes' list
            selected_index = processes.index(selected_process)
            
            # Non-Preemptive: runs to completion
            burst_time = selected_process['bt']
            
            completion_time = current_time + burst_time
            turnaround_time = completion_time - selected_process['at']
            waiting_time = turnaround_time - burst_time

            # Update process dictionary with results
            selected_process['ct'] = completion_time
            selected_process['tat'] = turnaround_time
            selected_process['wt'] = waiting_time
            
            # Update counters
            current_time = completion_time
            total_tat += turnaround_time
            total_wt += waiting_time
            completed_count += 1
            
            # Store result and remove from main list to avoid re-selection
            final_results[selected_process['original_index']] = selected_process
            del processes[selected_index]
        
        else:
            # CPU is idle. Advance time to the arrival time of the next process.
            next_arrival = float('inf')
            found_next = False
            for p in processes:
                if p['at'] > current_time and 'ct' not in p:
                    next_arrival = min(next_arrival, p['at'])
                    found_next = True
            
            if found_next:
                current_time = next_arrival
            else:
                break

    avg_tat = total_tat / n if n > 0 else 0
    avg_wt = total_wt / n if n > 0 else 0
    
    final_results.sort(key=lambda x: x['original_index'])
    _print_metrics_table("Priority Scheduling - Non-Preemptive (Lower number = Higher Priority)", final_results, avg_tat, avg_wt)


# ==============================================================================
# 5. Priority Scheduling - Preemptive (Lower number = Higher Priority)
# ==============================================================================

def priority_scheduling_preemptive(process_list, arrival_time_list, burst_time_list, priority_list):
    """Calculates metrics for Preemptive Priority scheduling."""
    if not (len(process_list) == len(arrival_time_list) == len(burst_time_list) == len(priority_list)):
        print("Error: All input lists must have the same length.")
        return

    # 1. Initialize Processes and Data
    processes = []
    for i, (p, at, bt, pri) in enumerate(zip(process_list, arrival_time_list, burst_time_list, priority_list)):
        processes.append({
            'name': p, 
            'at': at, 
            'bt': bt, 
            'rem_bt': bt, # Remaining Burst Time
            'priority': pri,
            'original_index': i
        })
    
    n = len(processes)
    completed_count = 0
    current_time = 0
    
    # Metrics
    total_tat = 0
    total_wt = 0
    
    final_results = [None] * n

    while completed_count < n:
        # 2. Identify the ready queue (arrived processes with remaining work)
        ready_queue = [p for p in processes if p['at'] <= current_time and p['rem_bt'] > 0]

        if not ready_queue:
            # CPU is idle. Advance time.
            next_arrival = float('inf')
            found_next = False
            for p in processes:
                if p['at'] > current_time and p['rem_bt'] > 0 and p['at'] < next_arrival:
                    next_arrival = p['at']
                    found_next = True
            
            if found_next:
                current_time = next_arrival
                continue
            else:
                break

        # 3. Select the Highest Priority process
        # Sort by Priority (priority), then Arrival Time (at) for tie-breaking
        ready_queue.sort(key=lambda x: (x['priority'], x['at']))
        selected_process = ready_queue[0]

        # 4. Execution (Run for 1 time unit)
        selected_process['rem_bt'] -= 1
        current_time += 1
        
        # 5. Check for Completion
        if selected_process['rem_bt'] == 0:
            
            completion_time = current_time
            turnaround_time = completion_time - selected_process['at']
            waiting_time = turnaround_time - selected_process['bt'] # Use original BT

            # Update process dictionary with results
            selected_process['ct'] = completion_time
            selected_process['tat'] = turnaround_time
            selected_process['wt'] = waiting_time
            
            # Update counters
            total_tat += turnaround_time
            total_wt += waiting_time
            completed_count += 1
            
            # Store result
            final_results[selected_process['original_index']] = selected_process
        
    # 6. Final Calculation and Display
    avg_tat = total_tat / n if n > 0 else 0
    avg_wt = total_wt / n if n > 0 else 0
    
    final_results.sort(key=lambda x: x['original_index'])
    _print_metrics_table("Priority Scheduling - Preemptive (Lower number = Higher Priority)", final_results, avg_tat, avg_wt)


# # ==============================================================================
# # --- Example Usage (How to call the functions) ---
# # ==============================================================================

# if __name__ == '__main__':
#     # Standard input data (used for FCFS, SJF, SRTN)
#     processes_std = ['P1', 'P2', 'P3', 'P4']
#     arrival_times_std = [0, 1, 2, 3]
#     burst_times_std = [6, 8, 7, 3]

#     # Input data including Priority (used for both Priority algorithms)
#     processes_pri = ['P_A', 'P_B', 'P_C', 'P_D']
#     arrival_times_pri = [0, 1, 2, 3]
#     burst_times_pri = [10, 5, 2, 4]
#     # Priority: Lower number means HIGHER priority
#     priority_list_pri = [2, 0, 1, 3] # P_B is highest (0), P_D is lowest (3)

#     print("--- 1. FCFS Demonstration ---")
#     fcfs_scheduling(processes_std, arrival_times_std, burst_times_std)

#     print("\n--- 2. SJF (Non-Preemptive) Demonstration ---")
#     sjf_scheduling_non_preemptive(processes_std, arrival_times_std, burst_times_std)

#     print("\n--- 3. SRTN (Preemptive) Demonstration ---")
#     srtn_scheduling_preemptive(processes_std, arrival_times_std, burst_times_std)

#     print("\n--- 4. Priority (Non-Preemptive) Demonstration ---")
#     priority_scheduling_non_preemptive(processes_pri, arrival_times_pri, burst_times_pri, priority_list_pri)

#     print("\n--- 5. Priority (Preemptive) Demonstration ---")
#     priority_scheduling_preemptive(processes_pri, arrival_times_pri, burst_times_pri, priority_list_pri)
