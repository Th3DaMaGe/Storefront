
from django.core.exceptions import ValidationError
def validate_file_size(file):
    max_size_kb = 90
    
    if file.size > max_size_kb * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_kb} KB!')