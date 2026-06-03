class MaterialModel {
  final int id;
  final String titulo;
  final String autor;
  final String editorial;
  final String categoria;
  final int anioPublicacion;
  final int cantidadDisponible;
  final String isbn;
  final String tipoDocumento;

  MaterialModel({
    required this.id,
    required this.titulo,
    required this.autor,
    required this.editorial,
    required this.categoria,
    required this.anioPublicacion,
    required this.cantidadDisponible,
    required this.isbn,
    required this.tipoDocumento,
  });

  factory MaterialModel.fromJson(Map<String, dynamic> json) {
    // Si autores es una lista, unirlos por comas. Si es un solo string, usarlo directamente.
    String parseAutor(dynamic val) {
      if (val == null) return 'Desconocido';
      if (val is List) {
        return val.join(', ');
      }
      return val.toString();
    }

    return MaterialModel(
      id: json['id_material'] ?? 0,
      titulo: json['titulo'] ?? 'Desconocido',
      autor: parseAutor(json['autores_id_autor']),
      editorial: json['editoriales_id_editorial'] ?? 'Desconocido',
      categoria: json['categorias_id_categoria'] ?? 'Desconocido',
      anioPublicacion: json['año_publicacion'] ?? 0,
      cantidadDisponible: json['cantidad_disponible'] ?? 0,
      isbn: json['isbn'] ?? 'No especificado',
      tipoDocumento: json['tipodocumento_id_tipo'] ?? 'No especificado',
    );
  }
}
