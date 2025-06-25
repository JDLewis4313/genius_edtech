# apps/blog/migrations/0003_externalarticle.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost'),  # Update this to your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('nasa', 'NASA'), ('noaa', 'NOAA'), ('nature', 'Nature'), ('science_daily', 'Science Daily'), ('mit_tech', 'MIT Technology Review'), ('chemistry_world', 'Chemistry World'), ('other', 'Other')], max_length=50)),
                ('source_name', models.CharField(max_length=100)),
                ('original_url', models.URLField(unique=True)),
                ('title', models.CharField(max_length=300)),
                ('summary', models.TextField()),
                ('featured_image', models.URLField(blank=True)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
                ('fetched_date', models.DateTimeField(auto_now_add=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('commentary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='external_articles', to='blog.blogpost')),
            ],
            options={
                'ordering': ['-published_date', '-fetched_date'],
            },
        ),
    ]
