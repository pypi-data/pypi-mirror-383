import math
import logging
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
from .utils import get_all_subordinates_optimized, get_all_distributors, get_last_locations

from apps.src.models import SpUserTracking, SpUsers, SpVisits, SpUserVisits, SpActivityLogs


logger = logging.getLogger(__name__)

def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points on Earth (km)."""
    R = 6371.0088
    phi1 = math.radians(lat1); phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlmb/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))


def _parse_date_local(date_str):
    """Parse YYYY-MM-DD to naive datetime range [start, end)."""
    try:
        naive = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None, None

    # Return naive datetime objects since USE_TZ is False
    start = naive
    end = start + timedelta(days=1)
    return start, end


def _query_tracks(user_id, date_str):
    """Query and return ordered, numeric track rows for one user, one day."""
    if not user_id or not date_str:
        return None, None, "Missing user_id or date."
    start, end = _parse_date_local(date_str)
    if not start:
        return None, None, "Invalid date format. Use YYYY-MM-DD."

    qs = (
        SpUserTracking.objects
        .filter(user_id=user_id, sync_date_time__gte=start, sync_date_time__lt=end)
        .exclude(latitude__isnull=True, longitude__isnull=True)
        .exclude(latitude="", longitude="")
        .order_by("sync_date_time")
        .values("latitude", "longitude", "accuracy", "velocity", "sync_date_time", "id", "status", "message")
    )

    points = []
    for row in qs:
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        except (TypeError, ValueError):
            continue
        points.append({
            "lat": lat,
            "lon": lon,
            "accuracy": row["accuracy"],
            "velocity": row["velocity"],
            "ts": row["sync_date_time"],
            "id": row["id"],
            "status": row["status"],
            "message": row["message"],
        })
    return points, (start, end), None


def _filter_poor_accuracy_points(points, max_accuracy_meters=50):
    """
    Filter out points with poor GPS accuracy first, as they're likely noise.
    Always keeps first and last points regardless of accuracy.
    """
    if len(points) <= 2:
        return points

    filtered = [points[0]]  # Always keep first point

    for i in range(1, len(points) - 1):
        point = points[i]
        accuracy = point.get("accuracy")

        # Keep point if accuracy is good or missing (assume good if not specified)
        if accuracy is None or accuracy <= max_accuracy_meters:
            filtered.append(point)

    # Always keep last point
    if points[-1] not in filtered:
        filtered.append(points[-1])

    return filtered


def _optimize_points_conservative(points, min_distance_meters=5):
    """
    Conservative optimization - only removes points that are extremely close together.
    Preserves track integrity by being very lenient with distance filtering.
    """
    if len(points) <= 3:
        return points

    optimized = [points[0]]  # Always keep first point

    for i in range(1, len(points) - 1):
        current = points[i]
        last_kept = optimized[-1]

        # Calculate distance from last kept point
        distance_m = _haversine_km(
            last_kept["lat"], last_kept["lon"],
            current["lat"], current["lon"]
        ) * 1000  # Convert to meters

        # Very conservative filtering - only remove if points are VERY close
        # and there's no significant change in other parameters
        should_keep = (
            distance_m >= min_distance_meters or  # Keep if moved at least 5 meters
            abs((current.get("velocity", 0) or 0) - (last_kept.get("velocity", 0) or 0)) > 1 or  # Velocity change
            current.get("status") != last_kept.get("status") or  # Status change
            abs((current.get("accuracy", 0) or 0) - (last_kept.get("accuracy", 0) or 0)) > 10  # Accuracy change
        )

        if should_keep:
            optimized.append(current)

    # Always keep last point
    if points[-1] not in optimized:
        optimized.append(points[-1])

    return optimized


def _build_geojson(points, user_id, date_str, optimize="conservative"):
    """FeatureCollection with a LineString + optimized point features."""
    if not points:
        return {"type": "FeatureCollection", "features": []}, 0.0

    # Apply optimization based on user preference
    if optimize == "none":
        optimized_points = points  # No optimization
    elif optimize == "aggressive":
        # More aggressive: stricter accuracy filter + larger distance threshold
        accuracy_filtered = _filter_poor_accuracy_points(points, max_accuracy_meters=30)
        optimized_points = _optimize_points_conservative(accuracy_filtered, min_distance_meters=10)
    else:  # conservative (default)
        # Conservative: filter poor accuracy + remove only very close points
        accuracy_filtered = _filter_poor_accuracy_points(points, max_accuracy_meters=100)
        optimized_points = _optimize_points_conservative(accuracy_filtered, min_distance_meters=3)

    # Use all original points for the line to maintain accuracy
    coords = [[p["lon"], p["lat"]] for p in points]

    # Calculate total distance using all points for accuracy
    total_km = 0.0
    for i in range(1, len(points)):
        total_km += _haversine_km(points[i-1]["lat"], points[i-1]["lon"], points[i]["lat"], points[i]["lon"])

    features = []

    # LineString using all points for smooth track
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {
            "user_id": user_id,
            "date": date_str,
            "points": len(points),
            "optimized_points": len(optimized_points),
            "total_distance_km": round(total_km, 3),
        },
    })

    # Add optimized individual points for interaction
    for p in optimized_points:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
            "properties": {
                "timestamp": p["ts"].isoformat() if p["ts"] else None,
                "accuracy": p["accuracy"],
                "velocity": p["velocity"],
                "id": p["id"],
                "status": p["status"],
                "message": p["message"],
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features,
    }, total_km


def _build_kml(points, user_id, date_str):
    """Return a KML string with a single LineString."""
    coords = "\n".join([f"{p['lon']},{p['lat']},0" for p in points])

    # Calculate total distance for KML description
    total_km = 0.0
    for i in range(1, len(points)):
        total_km += _haversine_km(points[i-1]["lat"], points[i-1]["lon"], points[i]["lat"], points[i]["lon"])

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>User {user_id} — {date_str}</name>
  <description>Total Distance: {round(total_km, 3)} km</description>
  <Placemark>
    <name>Track</name>
    <description>Total points: {len(points)}, Distance: {round(total_km, 3)} km</description>
    <Style>
      <LineStyle><color>ff0000ff</color><width>4</width></LineStyle>
    </Style>
    <LineString>
      <tessellate>1</tessellate>
      <coordinates>
{coords}
      </coordinates>
    </LineString>
  </Placemark>
</Document>
</kml>"""
    return kml


def user_day_track(request):
    """
    Endpoint: /tracks.geo?user_id=123&date=2025-10-09[&format=kml][&optimize=conservative|aggressive|none]
    - Default: GeoJSON (application/json)
    - If format=kml: KML (application/vnd.google-earth.kml+xml)
    - optimize=conservative (default): Filters poor accuracy + removes very close points
    - optimize=aggressive: More aggressive point reduction
    - optimize=none: No optimization (all points included)
    """
    user_id = request.GET.get("user_id")
    date_str = request.GET.get("date")
    fmt = (request.GET.get("format") or "geojson").lower()
    optimize = (request.GET.get("optimize") or "conservative").lower()

    points, _, err = _query_tracks(user_id, date_str)
    if err:
        return HttpResponseBadRequest(err)

    if not points:
        if fmt == "kml":
            # Return an empty but valid KML document
            empty_kml = _build_kml([], user_id or "unknown", date_str or "unknown")
            return HttpResponse(empty_kml, content_type="application/vnd.google-earth.kml+xml")
        return JsonResponse({"type": "FeatureCollection", "features": [], "meta": {"total_distance_km": 0.0}})

    if fmt == "kml":
        kml = _build_kml(points, user_id, date_str)
        return HttpResponse(kml, content_type="application/vnd.google-earth.kml+xml")

    geojson, total_km = _build_geojson(points, user_id, date_str, optimize)
    geojson["meta"] = {"total_distance_km": round(total_km, 3), "optimization": optimize}
    return JsonResponse(geojson)



def get_map_markers(user_id, date_str=None):
    logger.info(f"get_map_markers called for user_id: {user_id}, date_str: {date_str}")

    subordinate_ids = get_all_subordinates_optimized(user_id)
    subordinate_ids.append(int(user_id))  # Include the user themselves (convert to int)

    # Use provided date or default to today
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            logger.info(f"Using selected date for activity logs: {selected_date}")
        except ValueError:
            selected_date = datetime.now().date()
            logger.warning(f"Invalid date format {date_str}, using today: {selected_date}")
    else:
        selected_date = datetime.now().date()
        logger.info(f"No date provided, using today: {selected_date}")

    employees = {}

    # Get all employees at once
    try:
        # logger.info(f"Querying SpUsers with ids: {subordinate_ids}")
        employees_queryset = SpUsers.objects.filter(id__in=subordinate_ids).values(
            'id', 'first_name', 'last_name', 'emp_sap_id'
        ).order_by('first_name')
        logger.info(f"Found {employees_queryset.count()} employees in queryset")
    except Exception as e:
        logger.error(f"Error querying employees: {e}")
        employees_queryset = []

    # Get all employee IDs for bulk queries
    employee_ids = [emp['id'] for emp in employees_queryset]

    # Bulk fetch last locations for all employees (MySQL compatible)
    last_locations = {}
    try:
        # Get the latest sync_date_time for each employee first
        employee_ids_str = ','.join(map(str, employee_ids))  # Convert list to string
        latest_times = get_last_locations(
            employee_ids_str,
            selected_date,
            selected_date + timedelta(days=1)
        )

        # logger.info(f"Latest times fetched: {latest_times}")
        # Now get the actual records with those latest times
        if latest_times:
            for time_data in latest_times:
                user_id = time_data['user_id']
                last_locations[user_id] = {
                    "latitude": time_data['latitude'],
                    "longitude": time_data['longitude'],
                    "sync_date_time": time_data['sync_date_time'],
                }

        logger.info(f"Found last locations for {len(last_locations)} employees")
    except Exception as e:
        logger.info(f"Error querying last locations: {e}")

    # Bulk fetch all distributors for all employees
    distributors_by_emp = {}
    try:
        distributors = get_all_distributors(','.join(map(str, employee_ids)))

        for dist in distributors:
            emp_id = dist['reporting_to_emp_id']
            if emp_id not in distributors_by_emp:
                distributors_by_emp[emp_id] = []
            distributors_by_emp[emp_id].append(dist)

        total_distributors = sum(len(dists) for dists in distributors_by_emp.values())
        logger.info(f"Found {total_distributors} distributors across all employees")
    except Exception as e:
        logger.error(f"Error querying distributors: {e}")

    # Get all distributor IDs for bulk queries
    all_distributor_ids = []
    for dists in distributors_by_emp.values():
        all_distributor_ids.extend([d['id'] for d in dists])

    # Bulk fetch distributor visits for selected date
    distributor_visits_by_id = {}
    try:
        distributor_visits = SpUserVisits.objects.filter(
            user_id__in=all_distributor_ids,
            employee_id__in=employee_ids,
            checkin_datetime__date=selected_date
        ).values(
            'user_id', 'employee_id', 'checkin_datetime', 'checkout_datetime',
            'total_retail_time', 'latitude', 'longitude'
        )

        for visit in distributor_visits:
            key = (visit['user_id'], visit['employee_id'])
            if key not in distributor_visits_by_id:
                distributor_visits_by_id[key] = []
            distributor_visits_by_id[key].append({
                "checkin_datetime": visit['checkin_datetime'],
                "checkout_datetime": visit['checkout_datetime'],
                "total_retail_time": visit['total_retail_time'],
                "latitude": visit['latitude'],
                "longitude": visit['longitude'],
            })
        logger.info(f"Found {len(distributor_visits)} distributor visits for {selected_date}")
    except Exception as e:
        logger.error(f"Error querying distributor visits: {e}")

    # Bulk fetch all retailers for all distributors
    retailers_by_dist = {}
    try:
        retailers = SpUsers.objects.filter(
            reporting_to_id__in=all_distributor_ids
        ).values(
            'id', 'first_name', 'last_name', 'emp_sap_id', 'store_name',
            'latitude', 'longitude', 'created_at', 'reporting_to_id'
        )

        for retail in retailers:
            dist_id = retail['reporting_to_id']
            if dist_id not in retailers_by_dist:
                retailers_by_dist[dist_id] = []
            retailers_by_dist[dist_id].append(retail)

        total_retailers = sum(len(retailers) for retailers in retailers_by_dist.values())
        logger.info(f"Found {total_retailers} retailers across all distributors")
    except Exception as e:
        logger.error(f"Error querying retailers: {e}")

    # Get all retailer IDs for bulk queries
    all_retailer_ids = []
    for retailers in retailers_by_dist.values():
        all_retailer_ids.extend([r['id'] for r in retailers])

    # Bulk fetch retailer visits for selected date
    retailer_visits_by_id = {}
    try:
        retailer_visits = SpVisits.objects.filter(
            user_id__in=employee_ids,
            outlet_id__in=all_retailer_ids,
            checkin_datetime__date=selected_date
        ).values(
            'user_id', 'outlet_id', 'checkin_datetime', 'checkout_datetime', 'total_retail_time'
        )

        for visit in retailer_visits:
            key = (visit['user_id'], visit['outlet_id'])
            if key not in retailer_visits_by_id:
                retailer_visits_by_id[key] = []
            retailer_visits_by_id[key].append({
                "checkin_datetime": visit['checkin_datetime'],
                "checkout_datetime": visit['checkout_datetime'],
                "total_retail_time": visit['total_retail_time'],
            })
        logger.info(f"Found {len(retailer_visits)} retailer visits for {selected_date}")
    except Exception as e:
        logger.error(f"Error querying retailer visits: {e}")

    # Build the employees structure using pre-fetched data
    for emp in employees_queryset:
        employees[emp['id']] = {
            "id": emp['id'],
            "name": f"{emp['first_name']} {emp['last_name']}",
            "sap_id": emp['emp_sap_id'],
            "distributors": {}
        }

        # Add last location for employee marker
        if emp['id'] in last_locations:
            employees[emp['id']]['last_location'] = last_locations[emp['id']]
        else:
            employees[emp['id']]['last_location'] = None

        # Add distributors for this employee
        for dist in distributors_by_emp.get(emp['id'], []):
            employees[emp['id']]['distributors'][dist['id']] = {
                "id": dist['id'],
                "name": f"{dist['first_name']} {dist['last_name']}",
                "sap_id": dist['emp_sap_id'],
                "store_name": dist['store_name'],
                "latitude": dist['latitude'],
                "longitude": dist['longitude'],
                "employee_name": f"{emp['first_name']} {emp['last_name']}",
                "retailers": {}
            }

            # Add visits for this distributor
            visit_key = (dist['id'], emp['id'])
            visits = distributor_visits_by_id.get(visit_key, [])
            employees[emp['id']]['distributors'][dist['id']]['visits'] = visits
            employees[emp['id']]['distributors'][dist['id']]['is_visited_today'] = len(visits) > 0

            # Add retailers for this distributor
            retailer_list = retailers_by_dist.get(dist['id'], [])
            for retail in retailer_list:
                employees[emp['id']]['distributors'][dist['id']]['retailers'][retail['id']] = {
                    "id": retail['id'],
                    "name": f"{retail['first_name']} {retail['last_name']}",
                    "sap_id": retail['emp_sap_id'],
                    "store_name": retail['store_name'],
                    "latitude": retail['latitude'],
                    "longitude": retail['longitude'],
                    "created_at": retail.get('created_at'),
                    "is_created_today": retail.get('created_at') and retail.get('created_at').date() == selected_date,
                    "distributor_name": f"{dist['first_name']} {dist['last_name']}",
                    "employee_name": f"{emp['first_name']} {emp['last_name']}"
                }

                # Add retailer visits
                retailer_visit_key = (emp['id'], retail['id'])
                retailer_visit_list = retailer_visits_by_id.get(retailer_visit_key, [])
                employees[emp['id']]['distributors'][dist['id']]['retailers'][retail['id']]['visits'] = retailer_visit_list
                employees[emp['id']]['distributors'][dist['id']]['retailers'][retail['id']]['is_visited_today'] = len(retailer_visit_list) > 0

            # Add retailer count to distributor
            employees[emp['id']]['distributors'][dist['id']]['retailer_count'] = len(retailer_list)

    # Bulk fetch activity logs
    activity_markers = []
    try:
        activity_logs = SpActivityLogs.objects.select_related('user').filter(
            user_id__in=subordinate_ids,
            created_at__date=selected_date
        ).exclude(
            Q(latitude__isnull=True) | Q(latitude='') |
            Q(longitude__isnull=True) | Q(longitude='')
        ).values(
            'id', 'module', 'sub_module', 'heading', 'activity', 'user_id', 'user_name',
            'icon', 'platform', 'platform_icon', 'latitude', 'longitude', 'created_at'
        ).order_by('created_at')

        for log in activity_logs:
            activity_markers.append({
                "id": log['id'],
                "module": log['module'],
                "sub_module": log['sub_module'],
                "heading": log['heading'],
                "activity": log['activity'],
                "user_id": log['user_id'],
                "user_name": log['user_name'],
                "icon": log['icon'],
                "platform": log['platform'],
                "platform_icon": log['platform_icon'],
                "latitude": log['latitude'],
                "longitude": log['longitude'],
                "created_at": log['created_at'],
            })
        logger.info(f"Found {len(activity_markers)} activity logs for date {selected_date}")
    except Exception as e:
        logger.error(f"Error querying activity logs for date {selected_date}: {e}")

    logger.info(f"Successfully loaded {len(employees)} employees and {len(activity_markers)} activity markers for user {user_id}")
    logger.info(f"Function completed successfully")
    return {"employees": employees, "activity_markers": activity_markers}


# @login_required
def get_user_markers(request):
    """
    API endpoint to get markers for a specific user
    """
    logger.info(f"get_user_markers called with request method: {request.method}")
    logger.info(f"Request GET parameters: {request.GET}")

    user_id = request.GET.get("user_id")
    date_str = request.GET.get("date")  # Get the selected date
    logger.info(f"Extracted user_id: {user_id}, date_str: {date_str}")

    if not user_id:
        logger.warning("user_id parameter is missing")
        return JsonResponse({"error": "user_id is required"}, status=400)

    try:
        user_id = int(user_id)
        logger.info(f"Parsed user_id as integer: {user_id}")

        markers_data = get_map_markers(user_id, date_str)
        logger.info(f"Retrieved markers data with {len(markers_data.get('employees', {}))} employees and {len(markers_data.get('activity_markers', []))} activity markers")

        return JsonResponse(markers_data)
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid user_id format: {user_id}, error: {e}")
        return JsonResponse({"error": "Invalid user_id"}, status=400)
    except Exception as e:
        logger.error(f"Error in get_user_markers: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def track_map_page(request):
    """
    Page that renders the Google Map with full JS functionality.
    Usage (example):
      /track-view/?user_id=123&date=2025-10-09
    """
    user_id = request.GET.get("user_id", "")
    date_str = request.GET.get("date", "")

    user_ids = SpUserTracking.objects.values_list('user_id', flat=True).distinct()
    users = SpUsers.objects.filter(user_type=1).values('id', 'first_name', 'last_name', 'emp_sap_id').order_by('first_name')
    user_list = [{"id": u["id"], "name": f"{u['first_name']} {u['last_name']} (SAP: {u['emp_sap_id']})"} for u in users]

    return render(request, "salestrack/home.html", {"user_id": user_id, "date_str": date_str, "user_list": user_list})




