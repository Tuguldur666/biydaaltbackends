from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from api.settings import sendResponse, connectDB, disconnectDB
import os
from django.conf import settings

# Time Response Service
def dt_time(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"tsag":str(datetime.now())}]
    resp = sendResponse(action, 200, "Success", respData)
    return resp

# Hello World Service
def dt_hello(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"result":"Hello world"}]
    resp = sendResponse(action, 200, "Success", respData)
    return resp

# Class Info Service
def dt_class(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    respData = [{"result":"ISSW"}]
    resp = sendResponse(action, 200, "Success", respData)
    return resp

# Database Connection Check Service
def dt_connect_status(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    
    try:
        conn = connectDB()
        disconnectDB(conn)
        respData = [{"status": "DB connected successfully"}]
        resp = sendResponse(action, 200, "Success", respData)
    except Exception as e:
        respData = [{"status": "DB connection failed", "error": str(e)}]
        resp = sendResponse(action, 500, "Error", respData)
    
    return resp

# Add Movie Service
def dt_add_movie(request):
    action = request.POST.get('action')
    try:
        poster_file = request.FILES.get('poster')  
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        trailer = request.POST.get('trailer')
        release_date = request.POST.get('release_date')
        age_rate = request.POST.get('age_rate')
        movie_time = request.POST.get('time')
        rate = request.POST.get('rate')
        metascore = request.POST.get('metascore')
    except Exception as e: 
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{poster_file.name}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in poster_file.chunks():
                destination.write(chunk)

        destinationFilename = "media/uploads/" + filename

        query = """
            INSERT INTO t_movie (title, summary, poster, trailer, release_date, age_rate, "time", rate, metascore)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING movie_id
        """
        cursor.execute(query, (title, summary, destinationFilename, trailer, release_date, age_rate, movie_time, rate, metascore))
        movie_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_movie WHERE movie_id = %s"
        cursor.execute(query, (movie_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

# Add Category Service
def dt_add_category(request):
    try:
        request_json = json.loads(request.body)
        action = request_json.get("action")
        cat_name = request_json.get("cat_name")
        cat_color = request_json.get("cat_color")
        cat_desc = request_json.get("cat_desc")
    except Exception as e:
        respData = []
        resp = sendResponse("add_category", 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_category (cat_name, cat_color, cat_desc)
            VALUES (%s, %s, %s)
            RETURNING cat_id
        """
        cursor.execute(query, (cat_name, cat_color, cat_desc))
        cat_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_category WHERE cat_id = %s"
        cursor.execute(query, (cat_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action or "add_category", 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

# Add Actor Service
def dt_add_actor(request):
    action = request.POST.get('action')
    try:
        image = request.FILES.get('image')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.name}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/actors')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        destinationFilename = "media/uploads/actors/" + filename

        query = """
            INSERT INTO t_actor (image, fname, lname)
            VALUES (%s, %s, %s)
            RETURNING actor_id
        """
        cursor.execute(query, (destinationFilename, fname, lname))
        actor_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_actor WHERE actor_id = %s"
        cursor.execute(query, (actor_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

# Add Actor Relationship Service
def dt_add_actor_rel(request):
    request_json = json.loads(request.body)
    action = request_json('action')
    try:
        movie_id = request_json.get('movie_id')
        actor_id = request_json.get('actor_id')
        char_name = request_json.get('char_name')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_actor_rel (movie_id, actor_id, char_name)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        cursor.execute(query, (movie_id, actor_id, char_name))
        rel_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_actor_rel WHERE id = %s"
        cursor.execute(query, (rel_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

# Add Movie Content Service
def dt_add_movie_content(request):
    action = request.POST.get('action')
    try:
        movie_id = request.POST.get('movie_id')
        image = request.FILES.get('image')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.name}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/movie_content')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        destinationFilename = "media/uploads/movie_content/" + filename

        query = """
            INSERT INTO t_movie_content (movie_id, image)
            VALUES (%s, %s)
            RETURNING id
        """
        cursor.execute(query, (movie_id, destinationFilename))
        content_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_movie_content WHERE id = %s"
        cursor.execute(query, (content_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)
# 

# Add Genre Service
def dt_add_genre(request):
    request_json = json.loads(request.body)
    action = request_json.get('action')
    try:
        genre_name = request_json.get('genre_name')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_genre (genre_name)
            VALUES (%s)
            RETURNING genre_id
        """
        cursor.execute(query, (genre_name,))
        genre_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_genre WHERE genre_id = %s"
        cursor.execute(query, (genre_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)
# 
# Add Category-Movie Relationship Service
def dt_add_cat_movie(request):
    request_json = json.loads(request.body)
    action = request_json.get('action')
    try:
        movie_id = request_json.get('movie_id')
        cat_id = request_json.get('cat_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_cat_movie (movie_id, cat_id)
            VALUES (%s, %s)
            RETURNING id
        """
        cursor.execute(query, (movie_id, cat_id))
        rel_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_cat_movie WHERE id = %s"
        cursor.execute(query, (rel_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)
# 
# Add Wishlist Service
def dt_add_wishlist(request):

    action = request.POST.get('action')
    try:
        movie_id = request.POST.get('movie_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_wishlist (movie_id)
            VALUES (%s)
            RETURNING id
        """
        cursor.execute(query, (movie_id,))
        wishlist_id = cursor.fetchone()[0]
        myConn.commit()

        query = "SELECT * FROM t_wishlist WHERE id = %s"
        cursor.execute(query, (wishlist_id,))
        columns = cursor.description
        respRow = [{columns[index][0]: column for index, column in enumerate(row)} for row in cursor.fetchall()]

        resp = sendResponse(action, 200, "Success", respRow)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, "Database error: " + str(e), respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

# ///

def dt_get_all_movies(request):
    action = request.POST.get('action')
    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT m.*, g.genre_name, array_agg(DISTINCT c.cat_name) AS categories,
                   array_agg(DISTINCT a.fname || ' ' || a.lname || ' (' || ar.char_name || ')') AS actors
            FROM t_movie m
            LEFT JOIN t_genre g ON m.genre_id = g.genre_id
            LEFT JOIN t_cat_movie cm ON m.movie_id = cm.movie_id
            LEFT JOIN t_category c ON cm.cat_id = c.cat_id
            LEFT JOIN t_actor_rel ar ON m.movie_id = ar.movie_id
            LEFT JOIN t_actor a ON ar.actor_id = a.actor_id
            GROUP BY m.movie_id, g.genre_name
            ORDER BY m.movie_id DESC
        """
        cursor.execute(query)
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)
# ///

def dt_get_movies_by_cat(request):
    action = request.POST.get('action')
    cat_id = request.POST.get('cat_id')

    if not cat_id:
        return JsonResponse(sendResponse(action, 400, "cat_id is required", []))

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT m.* FROM t_movie m
            JOIN t_cat_movie cm ON m.movie_id = cm.movie_id
            WHERE cm.cat_id = %s
        """
        cursor.execute(query, (cat_id,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)
# ///

def dt_get_movie_detail(request):
    action = request.POST.get('action')
    movie_id = request.POST.get('movie_id')

    if not movie_id:
        return JsonResponse(sendResponse(action, 400, "movie_id is required", []))

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT m.*, g.genre_name,
                   array_agg(DISTINCT c.cat_name) AS categories,
                   array_agg(DISTINCT a.fname || ' ' || a.lname || ' as ' || ar.char_name) AS actors,
                   array_agg(DISTINCT mc.image) AS images
            FROM t_movie m
            LEFT JOIN t_genre g ON m.genre_id = g.genre_id
            LEFT JOIN t_cat_movie cm ON m.movie_id = cm.movie_id
            LEFT JOIN t_category c ON cm.cat_id = c.cat_id
            LEFT JOIN t_actor_rel ar ON m.movie_id = ar.movie_id
            LEFT JOIN t_actor a ON ar.actor_id = a.actor_id
            LEFT JOIN t_movie_content mc ON m.movie_id = mc.movie_id
            WHERE m.movie_id = %s
            GROUP BY m.movie_id, g.genre_name
        """
        cursor.execute(query, (movie_id,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)

@csrf_exempt
def checkService(request):
    if request.method != 'POST':
        resp = sendResponse("http_method", 405, "Method Not Allowed", [])
        return JsonResponse(resp)

    action = ''

    if request.content_type.startswith('application/json'):
        try:
            request_json = json.loads(request.body)
            action = request_json.get("action", "")
        except json.JSONDecodeError:
            resp = sendResponse("json_decode", 400, "Invalid JSON", [])
            return JsonResponse(resp)
    elif request.content_type.startswith('multipart/form-data'):
        action = request.POST.get("action", "")
    else:
        resp = sendResponse("content_type", 415, "Unsupported Media Type", [])
        return JsonResponse(resp)

    # Dispatch actions
    if action == 'class':
        return JsonResponse(dt_class(request))
    elif action == 'db_check':
        return JsonResponse(dt_connect_status(request))
    elif action == 'add_movie':
        return dt_add_movie(request)
    elif action == 'add_category':
        return dt_add_category(request)
    elif action == 'add_actor':
        return dt_add_actor(request)
    elif action == 'add_actor_rel':
        return dt_add_actor_rel(request)
    elif action == 'add_movie_content':
        return dt_add_movie_content(request)
    elif action == 'add_genre':
        return dt_add_genre(request)
    elif action == 'add_cat_movie':
        return dt_add_cat_movie(request)
    elif action == 'add_wishlist':
        return dt_add_wishlist(request)
    elif action == 'get_all_movies':
        return dt_get_all_movies(request)
    elif action == 'get_movies_by_cat':
        return dt_get_movies_by_cat(request)
    elif action == 'get_movie_detail':
        return dt_get_movie_detail(request)
    else:
        resp = sendResponse(action, 400, "Unknown action", [])
        return JsonResponse(resp)