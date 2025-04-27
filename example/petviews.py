from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from api.settings import sendResponse, connectDB, disconnectDB
import os
from django.conf import settings


# Helper function to send responses in a structured format
def sendResponse(action, code, message, data):
    return {
        "action": action,
        "status_code": code,
        "message": message,
        "data": data
    }


# 1. User Registration (dt_register)
def dt_register(request):
    action = request.POST.get('action')

    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
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
    action = request.POST.get('action')

    try:
        email = request.POST.get('email')
        password = request.POST.get('password')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT id, username, passwords FROM t_user WHERE email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and password:
            respData = [{"user_id": user[0], "username": user[1]}]
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


# 3. Add Pet Post (dt_add_pet)
def dt_add_pet(request):
    action = request.POST.get('action')

    try:
        name = request.POST.get('name')
        species_id = request.POST.get('species_id')
        breed_id = request.POST.get('breed_id')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        contact_info = request.POST.get('contact_info')
        posted_by = request.POST.get('posted_by')  # User who posts the pet
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        # Handle the image upload
        if image:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.name}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/pets')
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            destinationFilename = "media/uploads/pets/" + filename
        else:
            destinationFilename = ""

        # Insert pet post into database
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            INSERT INTO t_pets (name, species_id, breed_id, age, gender, description, image, contact_info, posted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        cursor.execute(query, (name, species_id, breed_id, age, gender, description, destinationFilename, contact_info, posted_by))
        pet_id = cursor.fetchone()[0]
        myConn.commit()

        respData = [{"pet_id": pet_id, "name": name}]
        resp = sendResponse(action, 200, "Pet post added successfully", respData)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 4. Get Pet Detail (dt_get_pet_detail)
def dt_get_pet_detail(request):
    action = request.POST.get('action')

    try:
        pet_id = request.POST.get('pet_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT p.id, p.name, p.age, p.gender, p.description, p.image, p.contact_info, 
                   s.name AS species_name, b.name AS breed_name
            FROM t_pets p
            JOIN t_species s ON p.species_id = s.id
            JOIN t_breeds b ON p.breed_id = b.id
            WHERE p.id = %s
        """
        cursor.execute(query, (pet_id,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 5. Update Pet Post (dt_update_pet)
def dt_update_pet(request):
    action = request.POST.get('action')

    try:
        pet_id = request.POST.get('pet_id')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        contact_info = request.POST.get('contact_info')
        is_adopted = request.POST.get('is_adopted', False)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            UPDATE t_pets SET name = %s, age = %s, gender = %s, description = %s, contact_info = %s, is_adopted = %s
            WHERE id = %s
        """
        cursor.execute(query, (name, age, gender, description, contact_info, is_adopted, pet_id))
        myConn.commit()

        respData = [{"pet_id": pet_id, "name": name}]
        resp = sendResponse(action, 200, "Pet post updated successfully", respData)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 6. Delete Pet Post (dt_delete_pet)
def dt_delete_pet(request):
    action = request.POST.get('action')

    try:
        pet_id = request.POST.get('pet_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = "DELETE FROM t_pets WHERE id = %s"
        cursor.execute(query, (pet_id,))
        myConn.commit()

        respData = [{"pet_id": pet_id}]
        resp = sendResponse(action, 200, "Pet post deleted successfully", respData)
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1006, f"Database error: {str(e)}", respData)
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 7. Get All Pets (dt_get_all_pets)
def dt_get_all_pets(request):
    action = request.POST.get('action')

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT p.id, p.name, p.age, p.gender, p.description, p.image, p.contact_info, 
                   s.name AS species_name, b.name AS breed_name
            FROM t_pets p
            JOIN t_species s ON p.species_id = s.id
            JOIN t_breeds b ON p.breed_id = b.id
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


# 8. Get Pets by Species (dt_get_pets_by_species)
def dt_get_pets_by_species(request):
    action = request.POST.get('action')

    try:
        species_id = request.POST.get('species_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT p.id, p.name, p.age, p.gender, p.description, p.image, p.contact_info, 
                   s.name AS species_name, b.name AS breed_name
            FROM t_pets p
            JOIN t_species s ON p.species_id = s.id
            JOIN t_breeds b ON p.breed_id = b.id
            WHERE p.species_id = %s
        """
        cursor.execute(query, (species_id,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 9. Get Pets by Breed (dt_get_pets_by_breed)
def dt_get_pets_by_breed(request):
    action = request.POST.get('action')

    try:
        breed_id = request.POST.get('breed_id')
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT p.id, p.name, p.age, p.gender, p.description, p.image, p.contact_info, 
                   s.name AS species_name, b.name AS breed_name
            FROM t_pets p
            JOIN t_species s ON p.species_id = s.id
            JOIN t_breeds b ON p.breed_id = b.id
            WHERE p.breed_id = %s
        """
        cursor.execute(query, (breed_id,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# 10. Get Pets by Adoption Status (dt_get_pets_by_adopted)
def dt_get_pets_by_adopted(request):
    action = request.POST.get('action')

    try:
        is_adopted = request.POST.get('is_adopted') == 'true'
    except Exception as e:
        respData = []
        resp = sendResponse(action, 1001, f"Request data missing or malformed: {str(e)}", respData)
        return JsonResponse(resp)

    try:
        myConn = connectDB()
        cursor = myConn.cursor()

        query = """
            SELECT p.id, p.name, p.age, p.gender, p.description, p.image, p.contact_info, 
                   s.name AS species_name, b.name AS breed_name
            FROM t_pets p
            JOIN t_species s ON p.species_id = s.id
            JOIN t_breeds b ON p.breed_id = b.id
            WHERE p.is_adopted = %s
        """
        cursor.execute(query, (is_adopted,))
        columns = cursor.description
        result = [{columns[i][0]: value for i, value in enumerate(row)} for row in cursor.fetchall()]
        resp = sendResponse(action, 200, "Success", result)
    except Exception as e:
        resp = sendResponse(action, 500, f"Database error: {str(e)}", [])
    finally:
        cursor.close()
        disconnectDB(myConn)

    return JsonResponse(resp)


# Route handler (checkService)
@csrf_exempt
def checkService(request):
    action = request.POST.get('action')

    if action == 'register':
        return dt_register(request)
    elif action == 'login':
        return dt_login(request)
    elif action == 'add_pet':
        return dt_add_pet(request)
    elif action == 'get_pet_detail':
        return dt_get_pet_detail(request)
    elif action == 'update_pet':
        return dt_update_pet(request)
    elif action == 'delete_pet':
        return dt_delete_pet(request)
    elif action == 'get_all_pets':
        return dt_get_all_pets(request)
    elif action == 'get_pets_by_species':
        return dt_get_pets_by_species(request)
    elif action == 'get_pets_by_breed':
        return dt_get_pets_by_breed(request)
    elif action == 'get_pets_by_adopted':
        return dt_get_pets_by_adopted(request)
    else:
        return JsonResponse({
            "action": action,
            "status_code": 1000,
            "message": "Invalid action",
            "data": []
        })
