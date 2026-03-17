import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../config.dart';
import '../services/api_service.dart';
import '../services/face_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameController = TextEditingController();
  final _passwordController = TextEditingController();
  final FaceService _faceService = FaceService();

  String? _nameError;
  String? _passwordError;
  String? _previewBase64;
  bool _loading = false;

  Future<void> _capturePhoto() async {
    setState(() {
      _nameError = _nameController.text.trim().isEmpty
          ? 'Informe o nome completo.'
          : null;
      _passwordError = _passwordController.text != Config.adminPassword
          ? 'Senha admin inválida.'
          : null;
    });

    if (_nameError != null || _passwordError != null) {
      return;
    }

    final granted = await _faceService.ensureCameraPermission();
    if (!granted) {
      _showMessage('Permissão de câmera negada.');
      return;
    }

    final cameras = await _faceService.loadCameras();
    if (cameras.isEmpty) {
      _showMessage('Nenhuma câmera disponível.');
      return;
    }

    final result = await Navigator.of(context).push<String>(
      MaterialPageRoute(
        builder: (_) => _RegisterCaptureScreen(
          camera: cameras.first,
          faceService: _faceService,
        ),
      ),
    );

    if (!mounted || result == null) {
      return;
    }

    setState(() {
      _previewBase64 = result;
    });
  }

  Future<void> _confirmRegister() async {
    if (_previewBase64 == null || _loading) {
      return;
    }

    setState(() {
      _loading = true;
    });

    try {
      final response = await ApiService.registerEmployee(
        _nameController.text.trim(),
        _previewBase64!,
      );
      _showMessage(
        response['message'] as String? ?? 'Funcionário cadastrado com sucesso.',
      );
      if (mounted) {
        Navigator.of(context).pop();
      }
    } on ApiException catch (error) {
      final code = error.payload?['error_code']?.toString();
      if (code == 'duplicate_face') {
        _showMessage('Este rosto já está cadastrado.');
      } else if (code == 'no_face_detected') {
        _showMessage('Nenhum rosto detectado na imagem enviada.');
      } else if (code == 'invalid_admin_password') {
        _showMessage('Senha admin inválida no backend.');
      } else {
        _showMessage(error.message);
      }
    } catch (_) {
      _showMessage('Erro inesperado ao cadastrar funcionário.');
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  void dispose() {
    _nameController.dispose();
    _passwordController.dispose();
    _faceService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cadastrar Funcionário')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: 'Nome completo',
              errorText: _nameError,
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _passwordController,
            obscureText: true,
            decoration: InputDecoration(
              labelText: 'Senha admin',
              errorText: _passwordError,
            ),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: _capturePhoto,
            icon: const Icon(Icons.photo_camera),
            label: const Text('Capturar Foto'),
          ),
          const SizedBox(height: 20),
          if (_previewBase64 != null) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF111827),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Text(
                'Foto capturada com sucesso. Confirme ou repita a captura.',
                style: TextStyle(color: Colors.white70),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _capturePhoto,
                    child: const Text('Repetir'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _loading ? null : _confirmRegister,
                    child: Text(_loading ? 'Enviando...' : 'Confirmar'),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _RegisterCaptureScreen extends StatefulWidget {
  const _RegisterCaptureScreen(
      {required this.camera, required this.faceService});

  final CameraDescription camera;
  final FaceService faceService;

  @override
  State<_RegisterCaptureScreen> createState() => _RegisterCaptureScreenState();
}

class _RegisterCaptureScreenState extends State<_RegisterCaptureScreen> {
  CameraController? _controller;
  bool _loading = true;
  bool _processing = false;
  String _status = 'Inicializando câmera...';

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );
    await _controller!.initialize();
    if (!mounted) {
      return;
    }
    setState(() {
      _loading = false;
      _status = 'Posicione o rosto e toque em confirmar.';
    });
  }

  Future<void> _capture() async {
    if (_controller == null ||
        !_controller!.value.isInitialized ||
        _processing) {
      return;
    }

    setState(() {
      _processing = true;
      _status = 'Analisando rosto...';
    });

    try {
      final file = await _controller!.takePicture();
      final capture = await widget.faceService.captureFaceBase64(file);
      if (!capture.faceDetected || capture.imageBase64 == null) {
        setState(() {
          _processing = false;
          _status = 'Nenhum rosto detectado. Tente novamente.';
        });
        return;
      }
      if (mounted) {
        Navigator.of(context).pop(capture.imageBase64);
      }
    } catch (error) {
      setState(() {
        _processing = false;
        _status = 'Erro ao capturar: $error';
      });
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Capturar Foto')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  width: double.infinity,
                  color: Colors.black,
                  child: _loading
                      ? const Center(child: CircularProgressIndicator())
                      : CameraPreview(_controller!),
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(_status, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _processing || _loading ? null : _capture,
                child:
                    Text(_processing ? 'Processando...' : 'Confirmar captura'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
