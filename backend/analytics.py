import pandas as pd
import os
from functools import lru_cache

# In-memory caching for large CSVs
_cache = {}

def get_data():
    if "hotels" not in _cache:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load hotels
        _cache["hotels"] = pd.read_csv(os.path.join(base_dir, 'hotels.csv'))
        
        # Load bookings (only required columns for speed/memory)
        # Handle exceptions if file missing
        try:
            _cache["bookings"] = pd.read_csv(os.path.join(base_dir, 'bookings.csv'), usecols=['property_id', 'revenue_realized'])
        except Exception:
            _cache["bookings"] = pd.DataFrame(columns=['property_id', 'revenue_realized'])
            
        try:
            _cache["occupancy"] = pd.read_csv(os.path.join(base_dir, 'occupancy.csv'), usecols=['property_id', 'successful_bookings', 'capacity'])
        except Exception:
            _cache["occupancy"] = pd.DataFrame(columns=['property_id', 'successful_bookings', 'capacity'])

    return _cache["hotels"], _cache["bookings"], _cache["occupancy"]

def get_revenue_by_city():
    df_hotels, df_bookings, _ = get_data()
    if df_bookings.empty or df_hotels.empty:
        return []
        
    merged = pd.merge(df_bookings, df_hotels, on='property_id')
    rev = merged.groupby('city')['revenue_realized'].sum().reset_index()
    
    return [{"name": str(row['city']), "revenue": int(row['revenue_realized'])} for _, row in rev.iterrows()]

def get_occupancy_by_city():
    df_hotels, _, df_occupancy = get_data()
    if df_occupancy.empty or df_hotels.empty:
        return []
        
    merged = pd.merge(df_occupancy, df_hotels, on='property_id')
    occ = merged.groupby('city')[['successful_bookings', 'capacity']].sum().reset_index()
    
    # Avoid division by zero
    occ['occupancy_rate'] = occ.apply(
        lambda r: (r['successful_bookings'] / r['capacity'] * 100) if r['capacity'] > 0 else 0, 
        axis=1
    )
    
    return [{"name": str(row['city']), "rate": round(float(row['occupancy_rate']), 2)} for _, row in occ.iterrows()]
