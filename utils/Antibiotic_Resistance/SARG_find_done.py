# checks sub-folders for results of resfinder
# =============================================

import os
import fnmatch

# Output files
done_file = "__SARG_done"
not_done_file = "__SARG_ndone"
# numbers
nr_ndone = 0
nr_done = 0


# Prepare output lists
done_folders = []
not_done_folders = []

# Get current directory
current_dir = os.getcwd()

# List all items in current directory
for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item,'ARO_SARG')
    # Check if it's a folder
    if os.path.isdir(item_path):
        # Look for results
        found = False
        for filename in os.listdir(item_path):
            if fnmatch.fnmatch(filename, "*tpm.type.txt"):
                found = True
                break

        if found:
            done_folders.append(item)
            #print(f"[DONE]     {item}")
            nr_done += 1
        else:
            not_done_folders.append(item)
            print(f"[NOT DONE] {item}")
            nr_ndone += 1

# Write results to output files
with open(done_file, "w") as f_done:
    for folder in done_folders:
        f_done.write(folder + "\n")

with open(not_done_file, "w") as f_not_done:
    for folder in not_done_folders:
        f_not_done.write(folder + "\n")

print("\nRGI results: DONE:",nr_done," / NOT DONE: ",nr_ndone,"\n Results written to '",done_file,"' and '",not_done_file,"'.")

