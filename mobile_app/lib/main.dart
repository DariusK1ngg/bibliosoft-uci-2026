import 'package:flutter/material.dart';
import 'screens/search_screen.dart';

void main() {
  runApp(const BibliosoftApp());
}

class BibliosoftApp extends StatelessWidget {
  const BibliosoftApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bibliosoft 2.0',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        primaryColor: Colors.indigo.shade800,
        scaffoldBackgroundColor: Colors.grey.shade100,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.indigo.shade800,
          foregroundColor: Colors.white,
          centerTitle: true,
        ),
        fontFamily: 'Roboto', // Familia de fuente genérica y limpia
      ),
      home: const SearchScreen(),
    );
  }
}
