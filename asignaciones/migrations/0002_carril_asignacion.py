# Migración generada manualmente
# Agrega el modelo Carril y actualiza Grupo con FK a Carril

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asignaciones', '0001_initial'),
        ('usuarios', '0002_nadador_rename_fecha_registro_usuario_created_at_and_more'),
    ]

    operations = [
        # 1. Agregar modelo Carril
        migrations.CreateModel(
            name='Carril',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField()),
                ('profundidad', models.DecimalField(decimal_places=2, max_digits=4)),
                ('capacidad_usuarios', models.IntegerField(default=10)),
                ('estado', models.CharField(
                    choices=[('disponible', 'Disponible'), ('ocupado', 'Ocupado'), ('mantenimiento', 'En Mantenimiento')],
                    default='disponible', max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('alberca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carriles', to='asignaciones.alberca')),
            ],
            options={
                'verbose_name': 'Carril',
                'verbose_name_plural': 'Carriles',
                'ordering': ['numero'],
                'unique_together': {('alberca', 'numero')},
            },
        ),

        # 2. Agregar campo carril a Grupo (opcional, puede ser null)
        migrations.AddField(
            model_name='grupo',
            name='carril',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='grupos',
                to='asignaciones.carril'
            ),
        ),

        # 3. Agregar campo turno a Grupo
        migrations.AddField(
            model_name='grupo',
            name='turno',
            field=models.CharField(
                choices=[('matutino', 'Matutino'), ('vespertino', 'Vespertino'), ('nocturno', 'Nocturno')],
                default='matutino', max_length=20
            ),
        ),

        # 4. Agregar campo activo a Grupo
        migrations.AddField(
            model_name='grupo',
            name='activo',
            field=models.BooleanField(default=True),
        ),

        # 5. Actualizar estado de Inscripcion a choices
        migrations.AlterField(
            model_name='inscripcion',
            name='estado',
            field=models.CharField(
                choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('suspendido', 'Suspendido')],
                default='activo', max_length=20
            ),
        ),

        # 6. Agregar unique_together a Inscripcion
        migrations.AlterUniqueTogether(
            name='inscripcion',
            unique_together={('nadador', 'grupo')},
        ),

        # 7. Agregar modelo Asignacion
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(
                    choices=[
                        ('lunes', 'Lunes'), ('martes', 'Martes'), ('miercoles', 'Miércoles'),
                        ('jueves', 'Jueves'), ('viernes', 'Viernes'), ('sabado', 'Sábado'), ('domingo', 'Domingo'),
                    ],
                    max_length=15
                )),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('fecha_inicio_vigencia', models.DateField()),
                ('fecha_fin_vigencia', models.DateField(blank=True, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('carril', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones', to='asignaciones.carril')),
                ('entrenador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones', to='usuarios.usuario')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones', to='asignaciones.grupo')),
            ],
            options={
                'verbose_name': 'Asignación',
                'verbose_name_plural': 'Asignaciones',
                'ordering': ['dia_semana', 'hora_inicio'],
            },
        ),
    ]