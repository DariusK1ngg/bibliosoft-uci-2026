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
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF004EA2),
          primary: const Color(0xFF004EA2),
        ),
        primaryColor: const Color(0xFF004EA2),
        scaffoldBackgroundColor: const Color(0xFFF0F4F9),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF004EA2),
          foregroundColor: Colors.white,
          centerTitle: true,
          elevation: 2,
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.0),
            side: const BorderSide(color: Color(0xFFE2E8F0), width: 1),
          ),
        ),
      ),
      home: const SearchScreen(),
    );
  }
}
