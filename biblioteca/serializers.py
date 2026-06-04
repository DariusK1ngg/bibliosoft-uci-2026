from rest_framework import serializers
from .models import Material, Categoria, Genero, Autor, Facultad, Carrera, Editorial

class MaterialSerializer(serializers.ModelSerializer):
    autores_id_autor = serializers.StringRelatedField(many=True)
    editoriales_id_editorial = serializers.StringRelatedField()
    categorias_id_categoria = serializers.StringRelatedField()
    tipodocumento_id_tipo = serializers.StringRelatedField()

    class Meta:
        model = Material
        fields = [
            'id_material', 'titulo', 'autores_id_autor', 'editoriales_id_editorial', 'categorias_id_categoria', 
            'tipodocumento_id_tipo', 'año_publicacion', 
            'cantidad_disponible', 'isbn', 'tipo_registro', 'numeracion_dewey'
        ]

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion']

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['id_genero', 'nombre']

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id_autor', 'nombre', 'apellido', 'descripcion']

class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = ['id_facultad', 'nombre']

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id_carrera', 'nombre', 'facultades_id_facultad']

class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editorial
        fields = ['id_editorial', 'nombre']
