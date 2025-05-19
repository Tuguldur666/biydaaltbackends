from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from api.settings import sendResponse, connectDB3, disconnectDB
import os
from django.conf import settings


def dt_register(request):
    request_json = json.loads(request.body)
    action = request_json.get('action')

    try:
        username = request_json.get('username')
        email = request_json.get('email')
        password = request_json.get('password')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB3()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_user (username, email, passwords)
            VALUES (%s, %s, %s) RETURNING id
        """
        cursor.execute(query, (username, email, password))
        user_id = cursor.fetchone()[0]
        myConn.commit()

        respData = [{"user_id": user_id, "username": username, "email": email}]
        resp = sendResponse(action, 200, "User registered successfully", respData)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 2. User Login (dt_login)
def dt_login(request):
    request_json = json.loads(request.body)
    action = request_json.get('action')

    try:
        email = request_json.get('email')
        password = request_json.get('password')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB3()
        cursor = myConn.cursor()

        query = """
            SELECT id, username, passwords , is_admin FROM t_user WHERE email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and password:
            respData = [{"user_id": user[0], "username": user[1], "is_admin":user[3]}]
            resp = sendResponse(action, 200, "Login successful", respData)
        else:
            respData = []
            resp = sendResponse(action, 400, "Invalid credentials", respData)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


def add_item(request):
    action = request.POST.get('action', 'add_item')
    print(f"[DEBUG] Incoming action: {action}")

    try:
        image_file = request.FILES.get('image')
        if not image_file:
            raise ValueError("Image file is required.")

        item_name = request.POST.get('item_name')
        item_price = request.POST.get('item_price')
        cat_id = request.POST.get('cat_id')

        print(f"[DEBUG] Form data: item_name={item_name}, item_price={item_price}, cat_id={cat_id}")

        if not item_name or not item_price or not cat_id:
            raise ValueError("All fields (item_name, item_price, cat_id) are required.")

    except Exception as e:
        print(f"[ERROR] Form parsing failed: {e}")
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", [])
        return JsonResponse(resp)

    try:
        myConn = connectDB3()
        cursor = myConn.cursor()
        print("[DEBUG] Database connection established.")

        # Save the image to disk with timestamped filename
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.name}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'items')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        destination_filename = f"media/items/{filename}"
        print(f"[DEBUG] Image saved to: {destination_filename}")

        # Insert item into DB
        query = """
            INSERT INTO t_item (item_name, item_price, image, cat_id)
            VALUES (%s, %s, %s, %s)
            RETURNING item_id
        """
        cursor.execute(query, (item_name, item_price, destination_filename, cat_id))
        item_id = cursor.fetchone()[0]
        myConn.commit()
        print(f"[DEBUG] Inserted item_id: {item_id}")

        # Fetch inserted item
        cursor.execute("SELECT item_id, item_name, item_price, image, cat_id FROM t_item WHERE item_id = %s", (item_id,))
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        respRow = [dict(zip(columns, row))] if row else []

        resp = sendResponse(action, 200, "Item added successfully", respRow)
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)
        print("[DEBUG] Database connection closed.")

    return JsonResponse(resp)

def get_all_categories(request):
    try:
        request_json = json.loads(request.body)
        action = request_json.get('action', 'get_all_categories')
    except Exception as e:
        action = "get_all_categories"
        return JsonResponse(sendResponse(action, 1001, f"Invalid JSON: {str(e)}", []))

    try:
        myConn = connectDB3()
        cursor = myConn.cursor()

        query = "SELECT cat_id, cat_name FROM t_category"
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        respData = [dict(zip(columns, row)) for row in rows]

        resp = sendResponse(action, 200, "Categories fetched successfully", respData)
    except Exception as e:
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

def get_item_by_catid(request):
    try:
        request_json = json.loads(request.body)
        action = request_json.get('action', 'getitembycatid')
        cat_id = request_json.get('cat_id')

        if not cat_id:
            return JsonResponse(sendResponse(action, 1001, "Missing 'cat_id' parameter", []))
    except Exception as e:
        return JsonResponse(sendResponse("getitembycatid", 1001, f"Invalid JSON: {str(e)}", []))

    try:
        myConn = connectDB3()
        cursor = myConn.cursor()

        query = """
            SELECT item_id, item_name, item_price, image, cat_id
            FROM t_item
            WHERE cat_id = %s
        """
        cursor.execute(query, (cat_id,))
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        respData = [dict(zip(columns, row)) for row in rows]

        resp = sendResponse(action, 200, "Items fetched successfully", respData)
    except Exception as e:
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


@csrf_exempt
def checkService(request):
    if request.method == "POST":
        content_type = request.content_type

        if content_type == 'application/json': 
            try:
                jsons = json.loads(request.body)
            except: 
                action = "invalid request json"
                respData = []
                resp = sendResponse(action, 404, "Error", respData)
                return JsonResponse(resp)

            try: 
                action = jsons['action']
            except:
                action = "no action"
                respData = []
                resp = sendResponse(action, 400, "Error", respData)
                return JsonResponse(resp)

            if action == 'register':
                return JsonResponse(dt_register(request))
            elif action == 'login':
                return JsonResponse(dt_login(request))
            elif action == 'getallcategory':
                return JsonResponse(get_all_categories(request))
            elif action == 'get_item_by_catid':
                return JsonResponse(get_item_by_catid(request))
            else:
                respData = []
                resp = sendResponse(action, 406, "Error", respData)
                return JsonResponse(resp)

        elif content_type.startswith('multipart/form-data'): 
            try: 
                action = request.POST.get('action')
            except:
                action = "no action"
                respData = []
                resp = sendResponse(action, 400, "no action key", respData)
                return JsonResponse(resp)

            if action == 'add_item':
                return add_item(request)
            else:
                respData = []
                resp = sendResponse(action, 406, "no registered action", respData)
                return JsonResponse(resp)

    elif request.method == "GET":
        return JsonResponse({"method": "GET"})

    else:
        return JsonResponse({"method": "busad"})
