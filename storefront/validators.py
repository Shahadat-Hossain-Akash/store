from django.core.exceptions import ValidationError

def max_image_file_size(file):
    max_size_in_mb = 2
    
    if file.size > max_size_in_mb * 1024 *1024:
        raise ValidationError(f'File size is greater than {max_size_in_mb}mb !')