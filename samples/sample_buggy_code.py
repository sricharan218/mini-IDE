"""Sample code with various code quality issues for ML-Powered IDE analysis."""

import os
import sys
import json
import math
import random
import hashlib
import datetime
import collections


# ═══════════════════════════════════════════════════════════════
# 🔴 HIGH RISK — Very complex function with deep nesting
# ═══════════════════════════════════════════════════════════════

def process_student_grades(students, courses, semester, config):
    results = {}
    errors = []
    total = 0
    count = 0
    flag = 0
    temp = 0
    x = 0
    
    for student in students:
        for course in courses:
            if student["enrolled"]:
                if course["active"]:
                    for grade in student["grades"]:
                        if grade["course_id"] == course["id"]:
                            if grade["score"] is not None:
                                if grade["score"] >= 0:
                                    if grade["score"] <= 100:
                                        if semester == "fall" or semester == "spring":
                                            total = total + grade["score"]
                                            count = count + 1
                                            temp = total
                                            x = count
                                            if grade["score"] < 60:
                                                flag = 1
                                                if config["notify"]:
                                                    try:
                                                        if config["email"]:
                                                            errors.append(student["name"])
                                                            flag = flag + 1
                                                    except:
                                                        pass
                                            results[student["name"]] = total / count
                                        else:
                                            errors.append("bad semester")
                                    else:
                                        errors.append("score too high")
                                else:
                                    errors.append("negative score")
                            else:
                                errors.append("null score")
    return results, errors


# ═══════════════════════════════════════════════════════════════
# 🔴 HIGH RISK — Long function with many responsibilities
# ═══════════════════════════════════════════════════════════════

def handle_user_request(request_data, db_connection, cache, logger):
    result = None
    status = "unknown"
    user = None
    data = None
    response = {}
    temp = None
    
    try:
        user_id = request_data.get("user_id")
        action = request_data.get("action")
        payload = request_data.get("payload", {})
        
        if not user_id:
            return {"error": "Missing user_id", "status": 400}
        
        if not action:
            return {"error": "Missing action", "status": 400}
        
        # Check cache
        cache_key = f"{user_id}:{action}"
        cached = cache.get(cache_key)
        if cached and action != "update" and action != "delete":
            return cached
        
        # Validate user
        user = db_connection.find_user(user_id)
        if not user:
            return {"error": "User not found", "status": 404}
        
        if user["banned"]:
            logger.warning(f"Banned user attempt: {user_id}")
            return {"error": "Account suspended", "status": 403}
        
        if user["role"] != "admin" and action in ["delete_all", "reset", "purge"]:
            return {"error": "Insufficient permissions", "status": 403}
        
        # Process actions
        if action == "create":
            data = payload.get("data")
            if not data:
                return {"error": "No data provided", "status": 400}
            result = db_connection.insert(data)
            status = "created"
            temp = result
            
        elif action == "read":
            item_id = payload.get("item_id")
            result = db_connection.find(item_id)
            if not result:
                return {"error": "Item not found", "status": 404}
            status = "ok"
            temp = result
            
        elif action == "update":
            item_id = payload.get("item_id")
            data = payload.get("data")
            old = db_connection.find(item_id)
            if not old:
                return {"error": "Item not found", "status": 404}
            result = db_connection.update(item_id, data)
            status = "updated"
            cache.invalidate(cache_key)
            temp = result
            
        elif action == "delete":
            item_id = payload.get("item_id")
            old = db_connection.find(item_id)
            if not old:
                return {"error": "Item not found", "status": 404}
            db_connection.delete(item_id)
            status = "deleted"
            cache.invalidate(cache_key)
            result = None
            temp = None
            
        elif action == "list":
            page = payload.get("page", 1)
            limit = payload.get("limit", 50)
            filters = payload.get("filters", {})
            sort_by = payload.get("sort", "created_at")
            result = db_connection.find_many(filters, sort_by, page, limit)
            status = "ok"
            temp = result
            
        elif action == "export":
            format_type = payload.get("format", "json")
            items = db_connection.find_all()
            if format_type == "json":
                result = json.dumps(items)
            elif format_type == "csv":
                result = ",".join(str(i) for i in items)
            status = "exported"
            temp = result
            
        else:
            return {"error": f"Unknown action: {action}", "status": 400}
        
        response = {
            "data": result,
            "status": status,
            "code": 200,
            "user": user_id,
            "timestamp": str(datetime.datetime.now()),
        }
        
        # Cache successful reads
        if action == "read" or action == "list":
            cache.set(cache_key, response, ttl=300)
        
        logger.info(f"Action {action} by {user_id}: {status}")
        return response
        
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e), "status": 500}


# ═══════════════════════════════════════════════════════════════
# 🟡 MEDIUM RISK — Moderate complexity with some issues
# ═══════════════════════════════════════════════════════════════

def calculate_statistics(data_points):
    n = len(data_points)
    total = 0
    total = sum(data_points)  # variable reuse
    mean = total / n
    
    variance = 0
    for x in data_points:
        diff = x - mean
        variance = variance + diff * diff  # variable reuse
    variance = variance / n
    
    std_dev = math.sqrt(variance)
    
    sorted_data = sorted(data_points)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]
    
    # Mode calculation
    freq = {}
    for x in data_points:
        if x in freq:
            freq[x] = freq[x] + 1
        else:
            freq[x] = 1
    
    mode = max(freq, key=freq.get)
    
    return {
        "mean": mean,
        "median": median,
        "mode": mode,
        "std_dev": std_dev,
        "variance": variance,
        "min": min(data_points),
        "max": max(data_points),
        "count": n,
    }


# ═══════════════════════════════════════════════════════════════
# 🟡 MEDIUM RISK — Multiple loops and exception handling
# ═══════════════════════════════════════════════════════════════

def merge_and_deduplicate(list_a, list_b, list_c):
    merged = []
    seen = set()
    
    for item in list_a:
        try:
            key = hashlib.md5(str(item).encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                merged.append(item)
        except Exception:
            pass
    
    for item in list_b:
        try:
            key = hashlib.md5(str(item).encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                merged.append(item)
        except Exception:
            pass
    
    for item in list_c:
        try:
            key = hashlib.md5(str(item).encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                merged.append(item)
        except Exception:
            pass
    
    merged.sort(key=lambda x: str(x))
    return merged


# ═══════════════════════════════════════════════════════════════
# 🟢 LOW RISK — Simple, clean function
# ═══════════════════════════════════════════════════════════════

def greet_user(name):
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to the ML-Powered IDE."


# ═══════════════════════════════════════════════════════════════
# 🟢 LOW RISK — Another clean function
# ═══════════════════════════════════════════════════════════════

def add_numbers(a, b):
    """Add two numbers together."""
    return a + b
