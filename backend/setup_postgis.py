#!/usr/bin/env python
"""
Quick setup script for PostGIS migration
This script will:
1. Check database connection
2. Create PostGIS extension if needed
3. Initialize database tables
4. Run migration
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def check_database_connection():
    """Check if we can connect to the database"""
    print("🔍 Checking database connection...")
    try:
        from database import engine
        connection = engine.connect()
        connection.close()
        print("   ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("\nPlease check your .env file and ensure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is correctly configured")
        print("  3. Database exists")
        return False

def check_postgis_extension():
    """Check if PostGIS extension is installed"""
    print("\n🔍 Checking PostGIS extension...")
    try:
        from database import engine
        with engine.connect() as connection:
            result = connection.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')"
            )
            has_postgis = result.scalar()
            if has_postgis:
                print("   ✅ PostGIS extension is installed")
                return True
            else:
                print("   ⚠️  PostGIS extension not found")
                print("\nAttempting to install PostGIS extension...")
                try:
                    connection.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                    connection.commit()
                    print("   ✅ PostGIS extension installed successfully")
                    return True
                except Exception as e:
                    print(f"   ❌ Failed to install PostGIS: {e}")
                    print("\nPlease run this SQL command manually as superuser:")
                    print("   CREATE EXTENSION postgis;")
                    return False
    except Exception as e:
        print(f"   ❌ Error checking PostGIS: {e}")
        return False

def initialize_tables():
    """Create database tables"""
    print("\n🔍 Initializing database tables...")
    try:
        from database import init_db
        init_db()
        print("   ✅ Database tables created")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create tables: {e}")
        return False

def run_migration():
    """Run the migration script"""
    print("\n🚀 Running migration...")
    try:
        from migrate_to_postgis import load_geojson_to_db
        
        geojson_path = os.path.join(backend_path, '../data/farms_final.geojson')
        if not os.path.exists(geojson_path):
            print(f"   ⚠️  GeoJSON file not found: {geojson_path}")
            print("   Skipping data migration. Tables are ready for new data.")
            return True
        
        load_geojson_to_db(geojson_path)
        return True
    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("   🚀 PostGIS Setup & Migration")
    print("=" * 60)
    
    # Check database connection
    if not check_database_connection():
        print("\n❌ Setup failed. Please fix database connection issues.")
        sys.exit(1)
    
    # Check PostGIS extension
    if not check_postgis_extension():
        print("\n❌ Setup failed. Please install PostGIS extension.")
        sys.exit(1)
    
    # Initialize tables
    if not initialize_tables():
        print("\n❌ Setup failed. Could not create database tables.")
        sys.exit(1)
    
    # Run migration
    print("\n" + "=" * 60)
    response = input("Do you want to migrate existing data now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        if run_migration():
            print("\n✅ Setup and migration complete!")
        else:
            print("\n⚠️  Setup complete but migration had issues.")
    else:
        print("\n✅ Setup complete! You can run migration later with:")
        print("   python backend/migrate_to_postgis.py")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. Start the API server: uvicorn main:app --reload")
    print("  2. Test the API: python test_postgis.py")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
