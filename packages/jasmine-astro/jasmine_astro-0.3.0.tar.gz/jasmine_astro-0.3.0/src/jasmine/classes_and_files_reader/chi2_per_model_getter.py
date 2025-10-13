import pandas as pd
import os
import glob

# Path to the main directory containing event folders
base_dir = '/Users/stela/Documents/teste/sample_rtmodel_v2.4'

# Keys that should get the "chi2_" prefix
chi2_keys = {"PS", "PX", "BS", "BO", "LS", "LX", "LO", "BestPlanetary", "BestBinary"}

data = []

for filepath in glob.glob(os.path.join(base_dir, "**", "Nature.txt"), recursive=True):
    event_name = os.path.basename(os.path.dirname(filepath))
    event_data = {"event_name_": event_name}

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if ":" in line:
                key, value = line.split(":", 1)
            elif "=" in line:
                key, value = line.split("=", 1)
            else:
                continue

            key = key.strip()
            value = value.strip()

            try:
                value = float(value)
            except ValueError:
                pass

            # Add "chi2_" prefix if the key is in our set
            if key in chi2_keys:
                new_key = f"{key}_chi2"
            else:
                new_key = key

            event_data[new_key] = value

    data.append(event_data)

df = pd.DataFrame(data)

df["Number of alternative models"] = df["Number of alternative models"].fillna(0).astype(int)


# Save to CSV
df.to_csv("/Users/stela/Documents/Scripts/orbital_task/RTModel_runs/sample_rtmodel_v2.4/nature_summary.csv", index=False)