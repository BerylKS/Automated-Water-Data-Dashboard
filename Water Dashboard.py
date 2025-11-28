import requests
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- CONFIGURATION ---
# We use the URL structure we discussed earlier.
# Site: 09504500 (Oak Creek at Sedalia, AZ)
# Parameter: 00060 (Streamflow)
# Period: P7D (Last 7 Days)
DATA_URL = "https://waterservices.usgs.gov/nwis/iv/?format=csv&sites=09504500&parameterCd=00060&period=P7D"

def fetch_usgs_data(url):
    """
    Fetches data from the USGS API and returns it as a Pandas DataFrame.
    """
    print(f"🌊 Connecting to USGS API...")
    response = requests.get(url)

    # Check if the request was successful (Status Code 200)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    
    print("✅ Data received successfully!")
    
    # USGS data usually has comment lines starting with '#'. 
    # We tell pandas to ignore those lines using comment='#'
    content = response.content.decode('utf-8')
    df = pd.read_csv(io.StringIO(content), comment='#', sep='\t')
    
    # The USGS returns a header row (agency_cd, site_no, datetime, tz_cd, values...)
    # We usually want to rename the messy value column to something readable.
    # Note: Column names vary, but usually the flow data is in the 5th column (index 4)
    # Let's inspect columns dynamically or rename standard columns.
    # For this specific API call, the flow value is usually named roughly '14788_00060'
    
    # A cleaner approach for this specific dashboard:
    # We drop the first row (which is often type info like "5s") 
    df = df.drop(0)
    
    # Rename columns for clarity
    # We assume standard output order: agency, site, datetime, timezone, flow_value, code
    df.columns = ['agency', 'site', 'datetime', 'timezone', 'flow_cfs', 'quality_flag']
    
    # Convert 'datetime' to a real datetime object so we can plot it
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Convert 'flow_cfs' to numeric (floats), forcing errors to NaN
    df['flow_cfs'] = pd.to_numeric(df['flow_cfs'], errors='coerce')
    
    return df

def analyze_data(df):
    """
    Calculates basic statistics for the river flow.
    """
    current_flow = df['flow_cfs'].iloc[-1]
    max_flow = df['flow_cfs'].max()
    min_flow = df['flow_cfs'].min()
    mean_flow = df['flow_cfs'].mean()
    
    print(f"\n📊 --- STATS FOR LAST 7 DAYS ---")
    print(f"Current Flow: {current_flow} cfs")
    print(f"Max Flow:     {max_flow} cfs")
    print(f"Min Flow:     {min_flow} cfs")
    print(f"Average Flow: {mean_flow:.2f} cfs")
    
    return current_flow, mean_flow

def plot_hydrograph(df):
    """
    Generates a hydrograph plot and saves it as an image.
    """
    print("\n🎨 Generating Hydrograph...")
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['datetime'], df['flow_cfs'], color='#1f77b4', linewidth=2, label='Streamflow')
    
    # Formatting the plot
    plt.title('Real-Time Streamflow: Oak Creek, AZ (Last 7 Days)', fontsize=14)
    plt.ylabel('Discharge ($ft^3/s$)', fontsize=12)
    plt.xlabel('Date & Time', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    filename = "hydrograph.png"
    plt.savefig(filename)
    print(f"💾 Plot saved as '{filename}'")
    plt.show() # Shows the plot if you are in an interactive environment

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        # 1. Get Data
        df_flow = fetch_usgs_data(DATA_URL)
        
        # 2. Analyze Data
        analyze_data(df_flow)
        
        # 3. Visualize Data
        plot_hydrograph(df_flow)
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")