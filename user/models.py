from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    name = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            img = img.convert('RGB')  # or any processing you need
            img_io = BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            self.image = InMemoryUploadedFile(img_io, None, self.image.name, 'image/jpeg', img_io.tell(), None)
        super().save(*args, **kwargs)
