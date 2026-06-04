import 'dart:async';
import 'package:flutter/material.dart';
import '../models/material_model.dart';
import '../services/api_service.dart';
import 'detail_screen.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({Key? key}) : super(key: key);

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();
  
  Future<List<MaterialModel>>? _materialesFuture;
  Timer? _debounce;

  // Filter choice lists (fetched from backend API)
  List<Map<String, dynamic>> _generos = [];
  List<Map<String, dynamic>> _facultades = [];
  List<Map<String, dynamic>> _carreras = [];
  bool _filtersLoaded = false;

  // Selected filter values
  String? _selectedGeneroId;
  String? _selectedAutorId;
  String? _selectedAutorName; // Stored selected author display name
  String? _selectedFacultadId;
  String? _selectedCarreraId;
  String? _selectedEditorialId;
  String? _selectedEditorialName; // Stored selected editorial display name
  bool _soloDisponibles = false;
  String? _selectedTipoRegistro;
  String? _selectedOrden = 'reciente';

  @override
  void initState() {
    super.initState();
    _materialesFuture = _apiService.fetchMateriales(orden: _selectedOrden);
    _loadFilters();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _loadFilters() async {
    try {
      final results = await Future.wait([
        _apiService.fetchGeneros(),
        _apiService.fetchFacultades(),
        _apiService.fetchCarreras(),
      ]);
      if (mounted) {
        setState(() {
          _generos = results[0];
          _facultades = results[1];
          _carreras = results[2];
          _filtersLoaded = true;
        });
      }
    } catch (e) {
      debugPrint("Error loading filters: $e");
    }
  }

  bool get _hasActiveFilters {
    return _selectedGeneroId != null ||
        _selectedAutorId != null ||
        _selectedFacultadId != null ||
        _selectedCarreraId != null ||
        _selectedEditorialId != null ||
        _soloDisponibles ||
        _selectedTipoRegistro != null ||
        (_selectedOrden != null && _selectedOrden != 'reciente');
  }

  List<Map<String, dynamic>> get _filteredCarreras {
    if (_selectedFacultadId == null || _selectedFacultadId!.isEmpty) {
      return _carreras;
    }
    return _carreras.where((c) => c['facultades_id_facultad'].toString() == _selectedFacultadId).toList();
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      _applyFilters();
    });
  }

  void _applyFilters() {
    setState(() {
      _materialesFuture = _apiService.fetchMateriales(
        query: _searchController.text,
        generoId: _selectedGeneroId,
        autorId: _selectedAutorId,
        facultadId: _selectedFacultadId,
        carreraId: _selectedCarreraId,
        editorialId: _selectedEditorialId,
        disponible: _soloDisponibles,
        tipoRegistro: _selectedTipoRegistro,
        orden: _selectedOrden,
      );
    });
  }

  void _clearFilters() {
    setState(() {
      _selectedGeneroId = null;
      _selectedAutorId = null;
      _selectedAutorName = null;
      _selectedFacultadId = null;
      _selectedCarreraId = null;
      _selectedEditorialId = null;
      _selectedEditorialName = null;
      _soloDisponibles = false;
      _selectedTipoRegistro = null;
      _selectedOrden = 'reciente';
    });
    _applyFilters();
  }

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

  Widget _buildMetaItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            color: Color(0xFF6B7280),
            fontSize: 10,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value.isNotEmpty && value != 'null' ? value : '—',
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            color: Color(0xFF1A2535),
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  void _showFilterBottomSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setModalState) {
            return Container(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
              ),
              padding: EdgeInsets.only(
                top: 20,
                left: 20,
                right: 20,
                bottom: MediaQuery.of(context).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Filtros de Búsqueda',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1A2535),
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            setModalState(() {
                              _selectedGeneroId = null;
                              _selectedAutorId = null;
                              _selectedAutorName = null;
                              _selectedFacultadId = null;
                              _selectedCarreraId = null;
                              _selectedEditorialId = null;
                              _selectedEditorialName = null;
                              _soloDisponibles = false;
                              _selectedTipoRegistro = null;
                              _selectedOrden = 'reciente';
                            });
                          },
                          child: const Text('Limpiar Todo'),
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 12),

                    // Tipo de Registro
                    const Text('Tipo de Material', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String?>(
                      value: _selectedTipoRegistro,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      hint: const Text('Todos los materiales'),
                      items: const [
                        DropdownMenuItem<String?>(value: null, child: Text('Todos los materiales')),
                        DropdownMenuItem<String?>(value: 'LIBRO', child: Text('Libros')),
                        DropdownMenuItem<String?>(value: 'TRABAJO_INVESTIGACION', child: Text('Trabajos de Investigación / Tesis')),
                        DropdownMenuItem<String?>(value: 'OTROS', child: Text('Otros Materiales')),
                      ],
                      onChanged: (val) {
                        setModalState(() {
                          _selectedTipoRegistro = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Facultad
                    const Text('Facultad', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String?>(
                      value: _selectedFacultadId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      hint: const Text('Todas las facultades'),
                      items: [
                        const DropdownMenuItem<String?>(value: null, child: Text('Todas las facultades')),
                        ..._facultades.map((f) => DropdownMenuItem<String?>(
                          value: f['id_facultad'].toString(),
                          child: Text(f['nombre']),
                        )),
                      ],
                      onChanged: (val) {
                        setModalState(() {
                          _selectedFacultadId = val;
                          _selectedCarreraId = null; // Reset carrera if faculty changes
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Carrera (Filtered dynamically)
                    const Text('Carrera', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String?>(
                      value: _selectedCarreraId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      hint: const Text('Todas las carreras'),
                      items: [
                        const DropdownMenuItem<String?>(value: null, child: Text('Todas las carreras')),
                        ..._filteredCarreras.map((c) => DropdownMenuItem<String?>(
                          value: c['id_carrera'].toString(),
                          child: Text(c['nombre']),
                        )),
                      ],
                      onChanged: (val) {
                        setModalState(() {
                          _selectedCarreraId = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Género
                    const Text('Género / Categoría', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String?>(
                      value: _selectedGeneroId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      hint: const Text('Todos los géneros'),
                      items: [
                        const DropdownMenuItem<String?>(value: null, child: Text('Todos los géneros')),
                        ..._generos.map((g) => DropdownMenuItem<String?>(
                          value: g['id_genero'].toString(),
                          child: Text(g['nombre']),
                        )),
                      ],
                      onChanged: (val) {
                        setModalState(() {
                          _selectedGeneroId = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Autor
                    const Text('Autor', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    Autocomplete<Map<String, dynamic>>(
                      key: Key('autor_ac_$_selectedAutorId'),
                      initialValue: TextEditingValue(text: _selectedAutorName ?? ''),
                      displayStringForOption: (option) => '${option['apellido'] ?? ''}, ${option['nombre'] ?? ''}',
                      optionsBuilder: (TextEditingValue textEditingValue) async {
                        if (textEditingValue.text.length < 2) {
                          return const Iterable<Map<String, dynamic>>.empty();
                        }
                        try {
                          return await _apiService.fetchAutores(search: textEditingValue.text);
                        } catch (e) {
                          return const Iterable<Map<String, dynamic>>.empty();
                        }
                      },
                      onSelected: (option) {
                        setModalState(() {
                          _selectedAutorId = option['id_autor'].toString();
                          _selectedAutorName = '${option['apellido']}, ${option['nombre']}';
                        });
                      },
                      fieldViewBuilder: (context, textEditingController, focusNode, onFieldSubmitted) {
                        return TextField(
                          controller: textEditingController,
                          focusNode: focusNode,
                          decoration: InputDecoration(
                            border: const OutlineInputBorder(),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            hintText: 'Escribe para buscar autor...',
                            suffixIcon: ValueListenableBuilder<TextEditingValue>(
                              valueListenable: textEditingController,
                              builder: (context, value, child) {
                                return value.text.isNotEmpty
                                    ? IconButton(
                                        icon: const Icon(Icons.clear, size: 18),
                                        onPressed: () {
                                          textEditingController.clear();
                                          setModalState(() {
                                            _selectedAutorId = null;
                                            _selectedAutorName = null;
                                          });
                                        },
                                      )
                                    : const SizedBox.shrink();
                              },
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),

                    // Editorial
                    const Text('Editorial', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    Autocomplete<Map<String, dynamic>>(
                      key: Key('editorial_ac_$_selectedEditorialId'),
                      initialValue: TextEditingValue(text: _selectedEditorialName ?? ''),
                      displayStringForOption: (option) => option['nombre'] ?? '',
                      optionsBuilder: (TextEditingValue textEditingValue) async {
                        if (textEditingValue.text.length < 2) {
                          return const Iterable<Map<String, dynamic>>.empty();
                        }
                        try {
                          return await _apiService.fetchEditoriales(search: textEditingValue.text);
                        } catch (e) {
                          return const Iterable<Map<String, dynamic>>.empty();
                        }
                      },
                      onSelected: (option) {
                        setModalState(() {
                          _selectedEditorialId = option['id_editorial'].toString();
                          _selectedEditorialName = option['nombre'];
                        });
                      },
                      fieldViewBuilder: (context, textEditingController, focusNode, onFieldSubmitted) {
                        return TextField(
                          controller: textEditingController,
                          focusNode: focusNode,
                          decoration: InputDecoration(
                            border: const OutlineInputBorder(),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            hintText: 'Escribe para buscar editorial...',
                            suffixIcon: ValueListenableBuilder<TextEditingValue>(
                              valueListenable: textEditingController,
                              builder: (context, value, child) {
                                return value.text.isNotEmpty
                                    ? IconButton(
                                        icon: const Icon(Icons.clear, size: 18),
                                        onPressed: () {
                                          textEditingController.clear();
                                          setModalState(() {
                                            _selectedEditorialId = null;
                                            _selectedEditorialName = null;
                                          });
                                        },
                                      )
                                    : const SizedBox.shrink();
                              },
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),

                    // Orden
                    const Text('Ordenar por', style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A2535))),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String?>(
                      value: _selectedOrden,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      hint: const Text('Más reciente'),
                      items: const [
                        DropdownMenuItem<String?>(value: 'reciente', child: Text('Año de publicación: Más reciente')),
                        DropdownMenuItem<String?>(value: 'antiguo', child: Text('Año de publicación: Más antiguo')),
                        DropdownMenuItem<String?>(value: 'agregado', child: Text('Fecha de ingreso: Agregado recientemente')),
                      ],
                      onChanged: (val) {
                        setModalState(() {
                          _selectedOrden = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Solo Disponibles Switch
                    SwitchListTile(
                      title: const Text(
                        'Solo Disponibles',
                        style: TextStyle(fontWeight: FontWeight.w600, fontSize: 15, color: Color(0xFF1A2535)),
                      ),
                      subtitle: const Text('Ocultar recursos sin stock en sala'),
                      value: _soloDisponibles,
                      contentPadding: EdgeInsets.zero,
                      activeColor: const Color(0xFF004EA2),
                      onChanged: (bool val) {
                        setModalState(() {
                          _soloDisponibles = val;
                        });
                      },
                    ),
                    const SizedBox(height: 24),

                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => Navigator.pop(context),
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('Cancelar'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () {
                              Navigator.pop(context);
                              _applyFilters();
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF004EA2),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: const Text('Aplicar Filtros'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildActiveFiltersWidget() {
    final List<Widget> chips = [];

    // Tipo Registro
    if (_selectedTipoRegistro != null) {
      String label = 'Libros';
      if (_selectedTipoRegistro == 'TRABAJO_INVESTIGACION') label = 'Tesis';
      if (_selectedTipoRegistro == 'OTROS') label = 'Otros';
      chips.add(_buildFilterChip(label, () {
        setState(() => _selectedTipoRegistro = null);
        _applyFilters();
      }));
    }

    // Facultad
    if (_selectedFacultadId != null) {
      final name = _facultades.firstWhere(
        (f) => f['id_facultad'].toString() == _selectedFacultadId,
        orElse: () => {'nombre': 'Facultad'},
      )['nombre'];
      chips.add(_buildFilterChip(name, () {
        setState(() {
          _selectedFacultadId = null;
          _selectedCarreraId = null;
        });
        _applyFilters();
      }));
    }

    // Carrera
    if (_selectedCarreraId != null) {
      final name = _carreras.firstWhere(
        (c) => c['id_carrera'].toString() == _selectedCarreraId,
        orElse: () => {'nombre': 'Carrera'},
      )['nombre'];
      chips.add(_buildFilterChip(name, () {
        setState(() => _selectedCarreraId = null);
        _applyFilters();
      }));
    }

    // Género
    if (_selectedGeneroId != null) {
      final name = _generos.firstWhere(
        (g) => g['id_genero'].toString() == _selectedGeneroId,
        orElse: () => {'nombre': 'Género'},
      )['nombre'];
      chips.add(_buildFilterChip(name, () {
        setState(() => _selectedGeneroId = null);
        _applyFilters();
      }));
    }

    // Autor
    if (_selectedAutorId != null) {
      chips.add(_buildFilterChip(_selectedAutorName ?? 'Autor', () {
        setState(() {
          _selectedAutorId = null;
          _selectedAutorName = null;
        });
        _applyFilters();
      }));
    }

    // Editorial
    if (_selectedEditorialId != null) {
      chips.add(_buildFilterChip(_selectedEditorialName ?? 'Editorial', () {
        setState(() {
          _selectedEditorialId = null;
          _selectedEditorialName = null;
        });
        _applyFilters();
      }));
    }

    // Solo Disponibles
    if (_soloDisponibles) {
      chips.add(_buildFilterChip('Disponibles', () {
        setState(() => _soloDisponibles = false);
        _applyFilters();
      }));
    }

    // Orden
    if (_selectedOrden != null && _selectedOrden != 'reciente') {
      String label = 'Orden: Antiguo';
      if (_selectedOrden == 'agregado') label = 'Orden: Agregado';
      chips.add(_buildFilterChip(label, () {
        setState(() => _selectedOrden = 'reciente');
        _applyFilters();
      }));
    }

    if (chips.isEmpty) return const SizedBox.shrink();

    return Container(
      height: 44,
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20),
        children: [
          // Clear all button chip
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ActionChip(
              avatar: const Icon(Icons.clear_all, size: 14, color: Colors.red),
              label: const Text('Limpiar', style: TextStyle(color: Colors.red, fontSize: 11)),
              backgroundColor: Colors.red.shade50,
              onPressed: _clearFilters,
            ),
          ),
          ...chips,
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, VoidCallback onDelete) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: InputChip(
        label: Text(
          label,
          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
        ),
        onDeleted: onDelete,
        deleteIconColor: Colors.black54,
        backgroundColor: const Color(0xFFF1F5F9),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFFCBD5E1)),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.account_balance, size: 24, color: Colors.white),
            SizedBox(width: 8),
            Text(
              'Biblio',
              style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: -0.5),
            ),
            Text(
              'soft',
              style: TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold, letterSpacing: -0.5),
            ),
          ],
        ),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Banner de Búsqueda (Hero Style)
          Container(
            width: double.infinity,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF004EA2), Color(0xFF003B7A)],
              ),
            ),
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Tag / Chip
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.search, size: 14, color: Colors.white),
                      SizedBox(width: 6),
                      Text(
                        'Búsqueda de Libros y Recursos',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Catálogo de Biblioteca',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Busca materiales disponibles en la biblioteca UCI',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 16),
                // Input de Búsqueda
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30.0),
                  ),
                  child: TextField(
                    controller: _searchController,
                    onChanged: _onSearchChanged,
                    style: const TextStyle(color: Color(0xFF1A2535), fontSize: 15),
                    decoration: InputDecoration(
                      hintText: 'Título, autor, categoría...',
                      hintStyle: const TextStyle(color: Colors.grey),
                      fillColor: Colors.white,
                      filled: true,
                      contentPadding: const EdgeInsets.symmetric(vertical: 12),
                      prefixIcon: const Icon(Icons.search, color: Color(0xFF004EA2)),
                      suffixIcon: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (_searchController.text.isNotEmpty)
                            IconButton(
                              icon: const Icon(Icons.clear, color: Colors.grey),
                              onPressed: () {
                                _searchController.clear();
                                _onSearchChanged('');
                              },
                            ),
                          Stack(
                            alignment: Alignment.center,
                            children: [
                              IconButton(
                                icon: Icon(
                                  _hasActiveFilters ? Icons.filter_alt : Icons.filter_alt_outlined,
                                  color: const Color(0xFF004EA2),
                                ),
                                onPressed: _showFilterBottomSheet,
                              ),
                              if (_hasActiveFilters)
                                Positioned(
                                  right: 8,
                                  top: 8,
                                  child: Container(
                                    padding: const EdgeInsets.all(2),
                                    decoration: const BoxDecoration(
                                      color: Colors.red,
                                      shape: BoxShape.circle,
                                    ),
                                    constraints: const BoxConstraints(
                                      minWidth: 8,
                                      minHeight: 8,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(width: 8),
                        ],
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30.0),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Listado de Filtros Activos (Chips horizontales)
          _buildActiveFiltersWidget(),
          
          // Contador de resultados
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            alignment: Alignment.centerLeft,
            child: FutureBuilder<List<MaterialModel>>(
              future: _materialesFuture,
              builder: (context, snapshot) {
                final count = snapshot.hasData ? snapshot.data!.length : 0;
                return Text(
                  'Se encontraron $count recurso(s)',
                  style: const TextStyle(
                    color: Color(0xFF6B7280),
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                );
              },
            ),
          ),
          
          // Resultados
          Expanded(
            child: FutureBuilder<List<MaterialModel>>(
              future: _materialesFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (snapshot.hasError) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 60, color: Colors.red),
                          const SizedBox(height: 16),
                          Text(
                            snapshot.error.toString(),
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 16),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () => _applyFilters(),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF004EA2),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20),
                              ),
                            ),
                            child: const Text('Reintentar'),
                          )
                        ],
                      ),
                    ),
                  );
                } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.menu_book, size: 80, color: Colors.grey.shade400),
                        const SizedBox(height: 16),
                        const Text(
                          'No se encontraron materiales',
                          style: TextStyle(fontSize: 18, color: Color(0xFF6B7280), fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Prueba a buscar con otros términos o filtros',
                          style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
                        ),
                      ],
                    ),
                  );
                }

                final materiales = snapshot.data!;

                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
                  itemCount: materiales.length,
                  itemBuilder: (context, index) {
                    final material = materiales[index];
                    final bool isAvailable = material.cantidadDisponible > 0;

                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                      clipBehavior: Clip.antiAlias,
                      child: InkWell(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => DetailScreen(material: material),
                            ),
                          );
                        },
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Top Bar (Side Panel in Web, Top Panel in Mobile)
                            Container(
                              color: const Color(0xFFF8FAFC),
                              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  // Icon + Badge format
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.all(6),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF004EA2).withOpacity(0.08),
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Icon(
                                          _getIconForType(material.tipoDocumento),
                                          color: const Color(0xFF004EA2),
                                          size: 16,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFFF1F5F9),
                                          borderRadius: BorderRadius.circular(50),
                                          border: Border.all(color: const Color(0xFFCBD5E1), width: 1),
                                        ),
                                        child: Text(
                                          material.tipoDocumento.toUpperCase(),
                                          style: const TextStyle(
                                            color: Color(0xFF475569),
                                            fontSize: 9,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  // Status Badge
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: isAvailable ? const Color(0xFFDCFCE7) : const Color(0xFFFEE2E2),
                                      borderRadius: BorderRadius.circular(50),
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(
                                          isAvailable ? Icons.check_circle : Icons.cancel,
                                          color: isAvailable ? const Color(0xFF15803D) : const Color(0xFFB91C1C),
                                          size: 12,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          isAvailable ? 'Disponible' : 'Sin stock',
                                          style: TextStyle(
                                            color: isAvailable ? const Color(0xFF15803D) : const Color(0xFFB91C1C),
                                            fontSize: 10,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Divider(height: 1, color: Color(0xFFE2E8F0)),
                            
                            // Body Panel
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    material.titulo,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      color: Color(0xFF1A2535),
                                      fontSize: 15,
                                      fontWeight: FontWeight.bold,
                                      height: 1.3,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'por ${material.autor}',
                                    style: const TextStyle(
                                      color: Color(0xFF6B7280),
                                      fontSize: 12.5,
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  
                                  // Metadata Grid
                                  Container(
                                    padding: const EdgeInsets.only(top: 12),
                                    decoration: const BoxDecoration(
                                      border: Border(
                                        top: BorderSide(color: Color(0xFFE2E8F0), width: 1),
                                      ),
                                    ),
                                    child: Column(
                                      children: [
                                        Row(
                                          children: [
                                            Expanded(child: _buildMetaItem('Género/Categoría', material.categoria)),
                                            Expanded(child: _buildMetaItem('Disponibles', '${material.cantidadDisponible} un.')),
                                          ],
                                        ),
                                        const SizedBox(height: 12),
                                        Row(
                                          children: [
                                            Expanded(child: _buildMetaItem('Editorial', material.editorial)),
                                            Expanded(child: _buildMetaItem('Año', material.anioPublicacion.toString())),
                                          ],
                                        ),
                                        const SizedBox(height: 12),
                                        Row(
                                          children: [
                                            Expanded(child: _buildMetaItem('ISBN/Código', material.isbn)),
                                            Expanded(child: _buildMetaItem('Dewey', material.numeracionDewey)),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
