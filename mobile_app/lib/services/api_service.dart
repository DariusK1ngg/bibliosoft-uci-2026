import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import '../models/material_model.dart';

class ApiService {
  Future<List<MaterialModel>> fetchMateriales({String query = ''}) async {
    final String url = query.isNotEmpty
        ? '${ApiConstants.baseUrl}/materiales/?search=$query'
        : '${ApiConstants.baseUrl}/materiales/';

    try {
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        // La paginación de DRF y ModelViewSets estándar puede devolver resultados en 'results'
        // Si no configuraste paginación en DRF, devuelve una lista directa.
        // Asumimos lista directa sin paginación, o si tiene paginación:
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
}
