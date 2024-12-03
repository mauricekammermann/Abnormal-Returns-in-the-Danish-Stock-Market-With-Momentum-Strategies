from constituents_data_processing import load_and_clean_data
from index_data_processing import load_and_clean_index_data
from snb_data_processing import load_and_clean_snb_data
from process_risk_free_yield import process_risk_free_yield
from pathlib import Path

if __name__ == "__main__":
    try:
        # Define the base path for file locations
        base_path = Path(__file__).resolve().parents[2]

        # Refinitiv Data of Constituents Processing
        print("Processing Constituents data...")
        constituents_file_path = base_path / "data" / "raw" / "SPI_Constituents_Data.xlsx"
        cleaned_consituents_df = load_and_clean_data(constituents_file_path)

        # Save Data of Constituents
        save_path_consituents = base_path / "data" / "processed" / "constituents_data.csv"
        cleaned_consituents_df.to_csv(save_path_consituents)
        print(f"Constituents data saved at {save_path_consituents}")

       # Data of Index Processing
        print("Processing Index data...")
        index_file_path = base_path / "data" / "raw" / "SPI_Index_Data.xlsx"
        cleaned_index_df = load_and_clean_index_data(index_file_path)

        # Save Data of Index 
        save_path_index = base_path / "data" / "processed" / "index_data.csv"
        cleaned_index_df.to_csv(save_path_index)
        print(f"Index data saved at {save_path_index}")

        # SNB Yield Data Processing
        print("\nProcessing SNB yield data...")
        snb_file_path = base_path / "data" / "raw" / "snb_yield_data.csv"
        cleaned_snb_df = load_and_clean_snb_data(snb_file_path)

        # Save SNB data 
        save_path_snb = base_path / "data" / "interim" / "snb_yield_data.csv"
        cleaned_snb_df.to_csv(save_path_snb, index=False)
        print(f"SNB yield data saved at {save_path_snb}")

        # Risk-Free Yield Processing
        print("\nProcessing risk-free yield data...")
        processed_risk_free = process_risk_free_yield(save_path_snb)  

        # Save Risk-Free Data to processed folder
        save_path_risk_free = base_path / "data" / "processed" / "risk_free.csv"
        processed_risk_free.to_csv(save_path_risk_free, index=False)
        print(f"Risk-free yield data saved at {save_path_risk_free}")

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
