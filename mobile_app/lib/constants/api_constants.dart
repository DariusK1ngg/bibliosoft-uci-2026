import 'package:flutter/foundation.dart';

class ApiConstants {
  // Si corre en la Web usa localhost, si corre en celular/emulador usa la IP de red o la de emulador
  static const String baseUrl = kIsWeb 
      ? 'http://localhost:8000/api' 
      : 'http://10.0.2.2:8000/api'; // Usa 'http://172.20.10.5:8000/api' si pruebas en celular físico
}
