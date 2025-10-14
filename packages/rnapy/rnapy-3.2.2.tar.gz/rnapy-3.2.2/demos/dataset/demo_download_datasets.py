from rnapy import RNAToolkit

# Initialize RNAToolkit
toolkit = RNAToolkit()

# List of available datasets
available_datasets = toolkit.list_available_datasets()
print("Available Datasets:")
for dataset in available_datasets:
    print(f" - {dataset}")

# Download specific datasets
toolkit.download_dataset("Rfam", max_workers=16)
toolkit.download_dataset("RNA_Puzzles")
toolkit.download_dataset("CASP15", max_workers=16)
toolkit.download_dataset("RNAsolo2", max_workers=16)
print("Datasets downloaded successfully.")