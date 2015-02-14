# django imports
from django.core.urlresolvers import reverse
from django.db import models


class CDDisc(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class CDCover(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class CD(models.Model):
    name = models.CharField(max_length=100, unique=True)
    disc = models.ImageField(
        upload_to='music.CDDisc/bytes/filename/mimetype',
        blank=True,
        null=True
    )
    cover = models.ImageField(
        upload_to='music.CDCover/bytes/filename/mimetype',
        blank=True,
        null=True
    )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cd.edit', kwargs={'pk': self.pk})
