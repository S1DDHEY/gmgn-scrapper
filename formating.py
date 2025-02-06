import csv

# Read the file and split into non-empty stripped lines
file_path = "./data/data.txt"
with open(file_path, "r", encoding="utf-8") as file:
    # Split lines and remove any that are blank after stripping whitespace
    lines = [line.strip() for line in file if line.strip()]

results = []

# Loop through the lines to find each occurrence of "Buy"
i = 0
while i < len(lines):
    # Check if the current line (or one that contains "Buy") qualifies.
    # (If "Buy" might have trailing spaces or be part of a line, you can change the condition.)
    if lines[i].lower() == "buy" or "buy" in lines[i].lower():
        # Ensure there are at least three more lines after "Buy"
        if i + 3 < len(lines):
            time_val = lines[i+1]
            address_line = lines[i+2]
            top10_val = lines[i+3]
            # Extract only the part of the address before "..."
            if "..." in address_line:
                address_val = address_line.split("...")[0]
            else:
                address_val = address_line
            results.append([time_val, address_val, top10_val])
            # Skip ahead so that we don't re-read overlapping entries.
            # (Assuming each occurrence is independent.)
            i += 4
            continue
    i += 1

# Write the results to a CSV file
csv_file_path = "./data/extracted_data.csv"
with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Time", "Address", "Top10"])  # Headers
    writer.writerows(results)

print(f"CSV file created successfully: {csv_file_path}")
