# file_upload/views.py
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5 MB
    if file.size > max_size:
        raise ValidationError(f'File size cannot exceed 5 MB.')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            
            # Validate file size
            validate_file_size(uploaded_file)
            
            # Generate a new encryption key
            key = Fernet.generate_key()
            fernet = Fernet(key)
            
            # Read and encrypt the file content
            file_content = uploaded_file.read()
            encrypted_content = fernet.encrypt(file_content)
            
            # Generate a unique filename
            filename = f"{uploaded_file.name}.encrypted"
            
            # Save the file using the default storage backend (S3 or local file system)
            file_path = default_storage.save(filename, ContentFile(encrypted_content))
            file_url = default_storage.url(file_path)
            
            # In a real application, you'd want to store the key securely, not return it
            return JsonResponse({
                'message': 'File uploaded successfully',
                'file_url': file_url,
                'encryption_key': key.decode()  # In production, store this securely!
            })
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred during file upload'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def upload_form(request):
    return render(request, 'file_upload/upload_form.html')