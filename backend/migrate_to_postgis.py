"""
Migration script to load existing GeoJSON data into PostGIS database
Run this once to migrate from file-based storage to database
"""
import json
import os
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from database import engine, Base, Farm, SessionLocal

def load_geojson_to_db(geojson_path: str):
    """Load farms from GeoJSON file into PostgreSQL/PostGIS"""
    
    # Create tables if they don't exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Load GeoJSON data
    print(f"Loading data from {geojson_path}...")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    features = geojson_data.get('features', [])
    print(f"Found {len(features)} farms to migrate")
    
    db = SessionLocal()
    try:
        # Clear existing data (optional - remove if you want to keep existing data)
        print("Clearing existing farm data...")
        db.query(Farm).delete()
        db.commit()
        
        migrated = 0
        skipped = 0
        
        for feature in features:
            props = feature['properties']
            geom = feature['geometry']
            
            # Check if farm already exists
            existing = db.query(Farm).filter(Farm.farm_id == str(props.get('farm_id'))).first()
            if existing:
                skipped += 1
                continue
            
            # Convert GeoJSON geometry to Shapely geometry
            shapely_geom = shape(geom)
            
            # Create farm record
            farm = Farm(
                farm_id=str(props.get('farm_id')),
                div_name=props.get('Div_Name'),
                vill_cd=props.get('Vill_Cd'),
                vill_name=props.get('Vill_Name'),
                vill_code=props.get('Vill_Code'),
                supervisor_name=props.get('Supervisor Name'),
                farmer_name=props.get('Farmer_Name'),
                father_name=props.get('Father_Name'),
                plot_no=props.get('Plot No'),
                gashti_no=props.get('Gashti No.'),
                survey_date=props.get('Survey Date'),
                area=props.get('Area'),
                shar=props.get('Shar'),
                varieties=props.get('Varieties'),
                crop_type=props.get('Crop Type'),
                east=props.get('East'),
                west=props.get('West'),
                north=props.get('North'),
                south=props.get('South'),
                wkt=props.get('WKT'),
                geometry=from_shape(shapely_geom, srid=4326),
                recent_date=props.get('recent_date'),
                recent_ndvi=props.get('recent_ndvi'),
                prev_date=props.get('prev_date'),
                prev_ndvi=props.get('prev_ndvi'),
                delta=props.get('delta'),
                harvest_flag=props.get('harvest_flag', 0)
            )
            
            db.add(farm)
            migrated += 1
            
            # Commit in batches of 100
            if migrated % 100 == 0:
                db.commit()
                print(f"Migrated {migrated} farms...")
        
        # Final commit
        db.commit()
        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated} farms")
        print(f"   Skipped: {skipped} farms (already existed)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()

def verify_migration(db: Session):
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    total_farms = db.query(Farm).count()
    print(f"   Total farms in database: {total_farms}")
    
    harvest_ready = db.query(Farm).filter(Farm.harvest_flag == 1).count()
    print(f"   Harvest ready farms: {harvest_ready}")
    
    villages = db.query(Farm.vill_name).distinct().count()
    print(f"   Unique villages: {villages}")
    
    avg_ndvi = db.query(Farm.recent_ndvi).filter(Farm.recent_ndvi.isnot(None)).all()
    if avg_ndvi:
        avg = sum([v[0] for v in avg_ndvi if v[0]]) / len(avg_ndvi)
        print(f"   Average NDVI: {avg:.3f}")

if __name__ == "__main__":
    # Path to your GeoJSON file
    geojson_path = os.path.join(os.path.dirname(__file__), '../data/farms_final.geojson')
    
    if not os.path.exists(geojson_path):
        print(f"❌ GeoJSON file not found: {geojson_path}")
        print("Please ensure the data file exists before running migration.")
        exit(1)
    
    print("=" * 60)
    print("   🚀 PostGIS Migration Script")
    print("=" * 60)
    
    load_geojson_to_db(geojson_path)
    
    # Verify
    db = SessionLocal()
    try:
        verify_migration(db)
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("   Migration complete! You can now remove the data folder dependency.")
    print("=" * 60)
