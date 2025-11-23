import argparse
from backend.services import ingest
import os

def main():
    parser = argparse.ArgumentParser(description="Process local CSV to GeoJSON.")
    parser.add_argument('--csv', required=True, help='Path to input CSV')
    parser.add_argument('--out', default='data/farms_final.geojson', help='Output GeoJSON path')
    parser.add_argument('--log', default='data/ingest.log', help='Log file path')
    args = parser.parse_args()

    n_ok, n_rej = ingest.csv_to_geojson(args.csv, args.out, args.log)
    print(f"Done. Processed: {n_ok}, Rejected: {n_rej}")
    print(f"GeoJSON written to: {args.out}")
    print(f"Log written to: {args.log}")

if __name__ == "__main__":
    main()
