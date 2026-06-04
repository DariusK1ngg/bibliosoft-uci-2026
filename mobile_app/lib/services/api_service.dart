import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import '../models/material_model.dart';

class ApiService {
  Future<List<MaterialModel>> fetchMateriales({
    String query = '',
    String? generoId,
    String? autorId,
    String? facultadId,
    String? carreraId,
    String? editorialId,
    bool? disponible,
    String? tipoRegistro,
    String? orden,
  }) async {
    final Map<String, String> queryParams = {};
    if (query.isNotEmpty) queryParams['search'] = query;
    if (generoId != null && generoId.isNotEmpty) queryParams['genero'] = generoId;
    if (autorId != null && autorId.isNotEmpty) queryParams['autor'] = autorId;
    if (facultadId != null && facultadId.isNotEmpty) queryParams['facultad'] = facultadId;
    if (carreraId != null && carreraId.isNotEmpty) queryParams['carrera'] = carreraId;
    if (editorialId != null && editorialId.isNotEmpty) queryParams['editorial'] = editorialId;
    if (disponible != null) queryParams['disponible'] = disponible ? '1' : '0';
    if (tipoRegistro != null && tipoRegistro.isNotEmpty) queryParams['tipo_registro'] = tipoRegistro;
    if (orden != null && orden.isNotEmpty) queryParams['orden'] = orden;

    final String queryString = Uri(queryParameters: queryParams).query;
    final String url = queryString.isNotEmpty
        ? '${ApiConstants.baseUrl}/materiales/?$queryString'
        : '${ApiConstants.baseUrl}/materiales/';

    try {
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        var decodedBody = json.decode(utf8.decode(response.bodyBytes));
        
        List<dynamic> data;
        if (decodedBody is Map && decodedBody.containsKey('results')) {
          data = decodedBody['results'];
        } else {
          data = decodedBody;
        }

        return data.map((item) => MaterialModel.fromJson(item)).toList();
      } else {
        throw Exception('Error al cargar materiales: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión. Verifica la IP y que el servidor Django esté corriendo.\nDetalle: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchGeneros({String search = ''}) async {
    try {
      final url = search.isNotEmpty
          ? '${ApiConstants.baseUrl}/generos/?search=${Uri.encodeComponent(search)}'
          : '${ApiConstants.baseUrl}/generos/';
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Error: ${response.statusCode}');
    } catch (e) {
      throw Exception('Error al cargar géneros: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchAutores({String search = ''}) async {
    try {
      final url = search.isNotEmpty
          ? '${ApiConstants.baseUrl}/autores/?search=${Uri.encodeComponent(search)}'
          : '${ApiConstants.baseUrl}/autores/';
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Error: ${response.statusCode}');
    } catch (e) {
      throw Exception('Error al cargar autores: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchFacultades() async {
    try {
      final response = await http.get(Uri.parse('${ApiConstants.baseUrl}/facultades/')).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Error: ${response.statusCode}');
    } catch (e) {
      throw Exception('Error al cargar facultades: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchCarreras() async {
    try {
      final response = await http.get(Uri.parse('${ApiConstants.baseUrl}/carreras/')).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Error: ${response.statusCode}');
    } catch (e) {
      throw Exception('Error al cargar carreras: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchEditoriales({String search = ''}) async {
    try {
      final url = search.isNotEmpty
          ? '${ApiConstants.baseUrl}/editoriales/?search=${Uri.encodeComponent(search)}'
          : '${ApiConstants.baseUrl}/editoriales/';
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.cast<Map<String, dynamic>>();
      }
      throw Exception('Error: ${response.statusCode}');
    } catch (e) {
      throw Exception('Error al cargar editoriales: $e');
    }
  }
}
