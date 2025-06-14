# Generated migration file for chemistry app
# Save this as: apps/chemistry/migrations/0002_update_element_fields.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chemistry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='phase',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_neutrons',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_protons',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_electrons',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_valence',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='radioactive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='element',
            name='natural',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='element',
            name='metal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='element',
            name='nonmetal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='element',
            name='metalloid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='element',
            name='first_ionization',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_isotopes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='discoverer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='specific_heat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='number_of_shells',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='element',
            name='block',
        ),
        migrations.RemoveField(
            model_name='element',
            name='electron_configuration',
        ),
        migrations.RemoveField(
            model_name='element',
            name='ionization_energy',
        ),
    ]
