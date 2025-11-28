"""
Test script to verify PostGIS migration is working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """Test if API is running"""
    print("\n1️⃣ Testing API health...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("   ✅ API is running")
        return True
    else:
        print("   ❌ API is not responding")
        return False

def test_farms_list():
    """Test listing farms"""
    print("\n2️⃣ Testing farms list endpoint...")
    response = requests.get(f"{BASE_URL}/farms?page=1&page_size=5")
    if response.status_code == 200:
        data = response.json()
        features = data.get('features', [])
        print(f"   ✅ Retrieved {len(features)} farms")
        if features:
            print(f"   Sample farm: {features[0]['properties']['farm_id']}")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False

def test_farm_by_id():
    """Test getting a single farm"""
    print("\n3️⃣ Testing single farm endpoint...")
    # First get a farm ID
    response = requests.get(f"{BASE_URL}/farms?page=1&page_size=1")
    if response.status_code == 200:
        features = response.json().get('features', [])
        if features:
            farm_id = features[0]['properties']['farm_id']
            response = requests.get(f"{BASE_URL}/farms/{farm_id}")
            if response.status_code == 200:
                farm = response.json()
                print(f"   ✅ Retrieved farm: {farm_id}")
                print(f"   Village: {farm['properties']['Vill_Name']}")
                print(f"   Area: {farm['properties']['Area']} ha")
                return True
    print("   ❌ Failed to get single farm")
    return False

def test_stats():
    """Test statistics endpoint"""
    print("\n4️⃣ Testing statistics endpoint...")
    response = requests.get(f"{BASE_URL}/stats/summary")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Statistics retrieved:")
        print(f"   Total farms: {stats['total_farms']}")
        print(f"   Harvest ready: {stats['harvest_ready_count']} ({stats['harvest_ready_percentage']:.1f}%)")
        print(f"   Avg NDVI: {stats['avg_ndvi']:.3f}")
        print(f"   Total area: {stats['total_area']:.2f} ha")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False

def test_charts():
    """Test chart endpoints"""
    print("\n5️⃣ Testing chart endpoints...")
    
    # Test NDVI by village
    response = requests.get(f"{BASE_URL}/charts/ndvi-by-village")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ NDVI by village: {len(data['labels'])} villages")
    else:
        print(f"   ❌ NDVI by village failed: {response.status_code}")
        return False
    
    # Test harvest area timeline
    response = requests.get(f"{BASE_URL}/charts/harvest-area-timeline")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Harvest area timeline: {len(data['labels'])} villages")
    else:
        print(f"   ❌ Harvest area timeline failed: {response.status_code}")
        return False
    
    return True

def test_harvest_chart():
    """Test harvest chart endpoint with different metrics"""
    print("\n6️⃣ Testing harvest chart endpoint...")
    
    metrics = ["area", "count", "percent"]
    for metric in metrics:
        response = requests.get(f"{BASE_URL}/harvest_chart/harvest-area-timeline?metric={metric}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Metric '{metric}': {len(data['labels'])} villages")
        else:
            print(f"   ❌ Metric '{metric}' failed: {response.status_code}")
            return False
    
    return True

def test_filters():
    """Test filtering by village"""
    print("\n7️⃣ Testing filters...")
    
    # Get stats for a specific village
    response = requests.get(f"{BASE_URL}/stats/summary?village=BAGHIGOVARDHAN PUR")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Filtered stats for village:")
        print(f"   Total farms: {stats['total_farms']}")
        print(f"   Harvest ready: {stats['harvest_ready_count']}")
        return True
    else:
        print(f"   ❌ Filter failed: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("   🧪 PostGIS Migration Test Suite")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  cd backend && uvicorn main:app --reload")
    print("\n" + "=" * 60)
    
    tests = [
        test_health,
        test_farms_list,
        test_farm_by_id,
        test_stats,
        test_charts,
        test_harvest_chart,
        test_filters
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"   Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! PostGIS migration is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the API logs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API. Make sure the server is running:")
        print("   cd backend && uvicorn main:app --reload")
