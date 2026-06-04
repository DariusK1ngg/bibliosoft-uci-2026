import 'package:flutter/material.dart';
import '../models/material_model.dart';

class DetailScreen extends StatelessWidget {
  final MaterialModel material;

  const DetailScreen({Key? key, required this.material}) : super(key: key);

  IconData _getIconForType(String type) {
    final t = type.toLowerCase();
    if (t.contains('libro')) {
      return Icons.book;
    } else if (t.contains('tesis') || t.contains('investigacion') || t.contains('trabajo')) {
      return Icons.school;
    } else if (t.contains('revista')) {
      return Icons.menu_book;
    } else {
      return Icons.description;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isAvailable = material.cantidadDisponible > 0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ficha Bibliográfica'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Hero Banner representing the book header
            Container(
              width: double.infinity,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFF004EA2), Color(0xFF003B7A)],
                ),
              ),
              padding: const EdgeInsets.fromLTRB(24, 24, 24, 32),
              child: Column(
                children: [
                  // Stylized Book Cover Icon
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white.withOpacity(0.2), width: 1.5),
                    ),
                    child: Icon(
                      _getIconForType(material.tipoDocumento),
                      color: Colors.white,
                      size: 36,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Title
                  Text(
                    material.titulo,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      height: 1.3,
                    ),
                  ),
                  const SizedBox(height: 8),
                  
                  // Author
                  Text(
                    'por ${material.autor}',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.85),
                      fontSize: 14,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
            
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Availability Banner Card
                  Card(
                    elevation: 0,
                    color: isAvailable ? const Color(0xFFDCFCE7) : const Color(0xFFFEE2E2),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            isAvailable ? Icons.check_circle : Icons.cancel,
                            color: isAvailable ? const Color(0xFF15803D) : const Color(0xFFB91C1C),
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            isAvailable 
                                ? 'Disponible para préstamo ($hasAvailableCount)'
                                : 'Sin stock disponible',
                            style: TextStyle(
                              color: isAvailable ? const Color(0xFF15803D) : const Color(0xFFB91C1C),
                              fontSize: 14.5,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  
                  const Text(
                    'DETALLES DEL RECURSO',
                    style: TextStyle(
                      color: Color(0xFF6B7280),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.8,
                    ),
                  ),
                  const SizedBox(height: 10),
                  
                  // Details Grid Card
                  Card(
                    elevation: 1,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          _buildDetailRow(Icons.class_, 'Clase de Material', material.tipoDocumento),
                          const Divider(height: 24, color: Color(0xFFE2E8F0)),
                          _buildDetailRow(Icons.category, 'Categoría / Género', material.categoria),
                          const Divider(height: 24, color: Color(0xFFE2E8F0)),
                          _buildDetailRow(Icons.business, 'Editorial', material.editorial),
                          const Divider(height: 24, color: Color(0xFFE2E8F0)),
                          _buildDetailRow(Icons.calendar_today, 'Año de Publicación', material.anioPublicacion.toString()),
                          const Divider(height: 24, color: Color(0xFFE2E8F0)),
                          _buildDetailRow(Icons.bookmark, 'ISBN / Código', material.isbn),
                          const Divider(height: 24, color: Color(0xFFE2E8F0)),
                          _buildDetailRow(Icons.filter_list, 'Numeración Dewey', material.numeracionDewey),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String get hasAvailableCount => '${material.cantidadDisponible} unidad(es)';

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF004EA2).withOpacity(0.06),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: const Color(0xFF004EA2), size: 20),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value.isNotEmpty && value != 'null' ? value : '—',
                style: const TextStyle(
                  color: Color(0xFF1A2535),
                  fontSize: 14.5,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        )
      ],
    );
  }
}
