from supabase import create_client

SUPABASE_URL = "https://qmwbvuspqepsmhirdgqk.storage.supabase.co/storage/v1/s3"
SUPABASE_KEY = "a95ee645c07e5e23e289f3d6b3b0edf5"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)