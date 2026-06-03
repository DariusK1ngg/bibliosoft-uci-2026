import 'package:flutter/material.dart';
import '../models/material_model.dart';

class DetailScreen extends StatelessWidget {
  final MaterialModel material;

  const DetailScreen({Key? key, required this.material}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ficha Bibliográfica'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Título
            Text(
              material.titulo,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            
            // Autor
            Text(
              'Autor: ${material.autor}',
              style: const TextStyle(
                fontSize: 18,
                color: Colors.grey,
                fontStyle: FontStyle.italic,
              ),
            ),
            const SizedBox(height: 24),

            // Tarjeta de detalles
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    _buildDetailRow(Icons.class_, 'Clase de Material', material.tipoDocumento),
                    const Divider(),
                    _buildDetailRow(Icons.business, 'Editorial', material.editorial),
                    const Divider(),
                    _buildDetailRow(Icons.category, 'Categoría', material.categoria),
                    const Divider(),
                    _buildDetailRow(Icons.calendar_today, 'A\u00f1o de Publicación', material.anioPublicacion.toString()),
                    const Divider(),
                    _buildDetailRow(Icons.bookmark, 'ISBN', material.isbn),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Disponibilidad
            Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: material.cantidadDisponible > 0 ? Colors.green.shade100 : Colors.red.shade100,
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(
                    color: material.cantidadDisponible > 0 ? Colors.green : Colors.red,
                    width: 2,
                  )
                ),
                child: Text(
                  material.cantidadDisponible > 0 
                      ? 'Stock Disponible: ${material.cantidadDisponible}' 
                      : 'NO DISPONIBLE',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: material.cantidadDisponible > 0 ? Colors.green.shade800 : Colors.red.shade800,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Colors.blueGrey, size: 28),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 14,
                  ),
                ),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
