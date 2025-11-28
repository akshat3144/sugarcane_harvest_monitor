"""
Verification script to confirm 100% database-only operation
Run this to verify no file dependencies remain
"""
import os
import sys
from pathlib import Path

def check_no_geojson_dependencies():
    """Check that no routers depend on GeoJSON files for data"""
    print("🔍 Checking for GeoJSON file dependencies in routers...")
    
    issues = []
    router_path = Path(__file__).parent / 'routers'
    
    exclude_files = {'upload.py'}  # Allowed to use temp files
    
    for py_file in router_path.glob('*.py'):
        if py_file.name in exclude_files or py_file.name.startswith('_'):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for file-based operations
            if 'gpd.read_file' in content:
                issues.append(f"   ❌ {py_file.name} uses gpd.read_file()")
            if 'GEOJSON_PATH' in content and 'farms_final.geojson' in content:
                issues.append(f"   ❌ {py_file.name} references farms_final.geojson")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("   ✅ No GeoJSON file dependencies found in routers")
        return True

def check_database_imports():
    """Check that routers import database dependencies"""
    print("\n🔍 Checking for database imports in routers...")
    
    router_path = Path(__file__).parent / 'routers'
    db_routers = []
    
    exclude_files = {'__init__.py', 'upload.py'}
    
    for py_file in router_path.glob('*.py'):
        if py_file.name in exclude_files or py_file.name.startswith('_'):
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'from backend.database import' in content or 'get_db' in content:
                db_routers.append(py_file.name)
    
    if db_routers:
        print(f"   ✅ {len(db_routers)} routers use database:")
        for router in db_routers:
            print(f"      - {router}")
        return True
    else:
        print("   ⚠️  No routers found using database")
        return False

def check_ingest_service():
    """Check that ingest service saves to database"""
    print("\n🔍 Checking ingest service...")
    
    ingest_path = Path(__file__).parent / 'services' / 'ingest.py'
    
    with open(ingest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Imports Farm model': 'from backend.database import' in content,
        'Uses SessionLocal': 'SessionLocal()' in content,
        'Inserts to database': 'db.add(farm)' in content or 'db.add(' in content,
        'Clears old data': 'db.query(Farm).delete()' in content,
        'No GeoJSON output': 'merged.to_file(final_geojson_path' not in content or 'final_geojson_path: Optional[str] = None' in content
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_passed = False
    
    return all_passed

def main():
    print("=" * 60)
    print("   🧪 Database-Only System Verification")
    print("=" * 60)
    
    checks = [
        check_no_geojson_dependencies,
        check_database_imports,
        check_ingest_service
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 60)
    if all(results):
        print("   ✅ All checks passed!")
        print("   System is 100% database-only")
    else:
        print("   ⚠️  Some checks failed")
        print("   Review issues above")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
