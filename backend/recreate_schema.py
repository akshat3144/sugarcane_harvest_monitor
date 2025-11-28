"""
Script to drop and recreate the farms table with the new schema
This will delete all existing data and create fresh tables
"""
from database import engine, Base, Farm

print("⚠️  WARNING: This will DELETE all existing data!")
print("Dropping existing tables...")

# Drop all tables
Base.metadata.drop_all(bind=engine)
print("✅ Old tables dropped")

# Create new tables with updated schema
Base.metadata.create_all(bind=engine)
print("✅ New tables created with updated schema")

print("\n" + "=" * 60)
print("Database schema has been updated!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: python backend/migrate_to_postgis.py")
print("   (to reload data from farms_final.geojson)")
print("2. Or upload new CSV through the API")
print("=" * 60)
