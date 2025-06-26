import os
import shutil
import pandas as pd
import geopandas as gpd
from datetime import datetime
from multiprocessing import cpu_count

from madina.una.workflows import betweenness_flow_simulation

def run_test_with_user_data(data_folder, pairings_file, base_output_folder):
    """
    Runs the betweenness flow simulation with user-provided data and validates the output.
    """
    try:
        # Create a timestamped subfolder for the output to avoid overwriting previous runs
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M")
        output_folder = os.path.join(base_output_folder, timestamp)

        # It's good practice to start with a clean output directory for a test run.
        if os.path.exists(output_folder):
            print(f"Output folder already exists. Removing it for a clean run: {output_folder}")
            shutil.rmtree(output_folder)
        
        print(f"Creating new output folder: {output_folder}")
        os.makedirs(output_folder)

        # Run the main workflow function
        print("Starting betweenness flow simulation...")
        betweenness_flow_simulation(
            # city_name is not needed because we are providing the full data and output paths
            data_folder=data_folder,
            output_folder=output_folder,
            pairings_file=pairings_file,  # This should be the filename, not the full path
            num_cores=cpu_count()
        )   
        print("Simulation finished.")

        # --- Verification Step ---
        print("Verifying results...")
        output_file = os.path.join(output_folder, "betweenness_record.geojson")
        assert os.path.exists(output_file), f"Output GeoJSON not created at {output_file}."
        
        result_gdf = gpd.read_file(output_file)
        assert not result_gdf.empty, "Output GeoJSON is empty."
        
        # Check if the flow column from the pairings file was added to the results
        pairings_df = pd.read_csv(os.path.join(data_folder, pairings_file))
        expected_flow_column = pairings_df.iloc[0]['Flow_Name']
        assert expected_flow_column in result_gdf.columns, f"Expected flow column '{expected_flow_column}' not found in the output file."
        
        # Check that some betweenness was actually calculated
        assert result_gdf[expected_flow_column].sum() > 0, f"Betweenness values in column '{expected_flow_column}' are all zero."

        print("✅ OD Pairing workflow test with user data completed successfully!")
        print(f"Check your results in: {output_folder}")

    except Exception as e:
        print(f"❌ An error occurred during the test run: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 1. Provide the absolute or relative path to the folder containing your data.
    #    This folder should contain your network, origins, and destinations GeoJSONs.
    DATA_FOLDER_PATH = "C:/Users/camer/Documents/UG Thesis/data/trip data/termini flows/Madina Notebooks/Cities/Hamilton/data"

    # 2. Provide the name of your pairings file, which must be inside the data folder.
    PAIRINGS_FILENAME = "pairings.csv"

    # 3. Provide a path for the base output folder. A new timestamped subfolder will be created inside it for each run.
    OUTPUT_FOLDER_PATH = "C:/Users/camer/Documents/UG Thesis/data/trip data/termini flows/Madina Notebooks/Cities/Hamilton/Simulations"
    
    # =================================================================================

    run_test_with_user_data(
        data_folder=DATA_FOLDER_PATH,
        pairings_file=PAIRINGS_FILENAME,
        base_output_folder=OUTPUT_FOLDER_PATH
    ) 