from distutils.command.upload import upload
from email.mime import image
from pyexpat import model
from tkinter import CASCADE
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    
    name = models.CharField(
        max_length=150,
        verbose_name='Название рецепта',
    )
    
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение рецепта',
    )
    
    description = models.CharField(
        max_length=255,
        verbose_name='Описание рецепта',
    )
    

