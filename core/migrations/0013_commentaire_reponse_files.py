from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_alter_publicationvideo_video_publicationpdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentaire',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='commentaires/images/'),
        ),
        migrations.AddField(
            model_name='commentaire',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='commentaires/videos/'),
        ),
        migrations.AddField(
            model_name='commentaire',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='commentaires/pdfs/'),
        ),
        migrations.AddField(
            model_name='reponse',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='reponses/images/'),
        ),
        migrations.AddField(
            model_name='reponse',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='reponses/videos/'),
        ),
        migrations.AddField(
            model_name='reponse',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='reponses/pdfs/'),
        ),
    ]
