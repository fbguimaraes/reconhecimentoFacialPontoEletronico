import 'package:flutter/material.dart';

import 'recognition_screen.dart';
import 'register_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Ponto Eletrônico'),
        actions: [
          IconButton(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const RegisterScreen()),
              );
            },
            icon: const Icon(Icons.person_add_alt_1),
            tooltip: 'Cadastrar funcionário',
          ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Reconhecimento Facial',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Escolha o tipo de registro',
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 16),
              ),
              const SizedBox(height: 48),
              _ActionButton(
                label: 'Registrar Entrada',
                icon: Icons.login,
                color: const Color(0xFF16A34A),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const RecognitionScreen(tipo: 'entrada'),
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
              _ActionButton(
                label: 'Registrar Saída',
                icon: Icons.logout,
                color: const Color(0xFFDC2626),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const RecognitionScreen(tipo: 'saida'),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 22),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
        ),
        onPressed: onTap,
        icon: Icon(icon, size: 28),
        label: Text(label),
      ),
    );
  }
}
