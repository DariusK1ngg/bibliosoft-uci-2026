from rest_framework import serializers
from .models import Material, Categoria

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
            'cantidad_disponible'
        ]

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'descripcion']
