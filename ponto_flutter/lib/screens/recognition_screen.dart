import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/face_service.dart';

class RecognitionScreen extends StatefulWidget {
  const RecognitionScreen({super.key, required this.tipo});

  final String tipo;

  @override
  State<RecognitionScreen> createState() => _RecognitionScreenState();
}

class _RecognitionScreenState extends State<RecognitionScreen>
    with WidgetsBindingObserver {
  final FaceService _faceService = FaceService();
  CameraController? _controller;
  bool _loading = true;
  bool _processing = false;
  String _status = 'Inicializando câmera...';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initialize();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) {
      return;
    }
    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused) {
      controller.dispose();
      _controller = null;
    } else if (state == AppLifecycleState.resumed) {
      _initialize();
    }
  }

  Future<void> _initialize() async {
    final granted = await _faceService.ensureCameraPermission();
    if (!granted) {
      setState(() {
        _status = 'Permissão de câmera negada.';
        _loading = false;
      });
      return;
    }

    final cameras = await _faceService.loadCameras();
    if (cameras.isEmpty) {
      setState(() {
        _status = 'Nenhuma câmera disponível.';
        _loading = false;
      });
      return;
    }

    final selected = _faceService.pickFrontOrFirstCamera(cameras);
    if (selected == null) {
      setState(() {
        _status = 'Nenhuma câmera disponível.';
        _loading = false;
      });
      return;
    }

    try {
      _controller?.dispose();
      _controller = CameraController(
        selected,
        ResolutionPreset.medium,
        enableAudio: false,
      );
      await _controller!.initialize();
    } catch (error) {
      setState(() {
        _status = 'Falha ao iniciar câmera: $error';
        _loading = false;
      });
      return;
    }

    if (!mounted) {
      return;
    }

    setState(() {
      _loading = false;
      _status = 'Posicione o rosto e toque em capturar.';
    });
  }

  Future<void> _captureAndRecognize() async {
    if (_controller == null ||
        !_controller!.value.isInitialized ||
        _processing) {
      return;
    }

    setState(() {
      _processing = true;
      _status = 'Capturando imagem...';
    });

    try {
      final file = await _controller!.takePicture();
      final capture = await _faceService.captureFaceBase64(file);
      if (!capture.faceDetected || capture.imageBase64 == null) {
        _showSnack('❌ Nenhum rosto detectado');
        setState(() {
          _processing = false;
          _status = 'Nenhum rosto detectado. Tente novamente.';
        });
        return;
      }

      setState(() {
        _status = 'Reconhecendo funcionário...';
      });
      final result = await ApiService.recognizeImage(capture.imageBase64!);

      if (result['recognized'] == true &&
          result['employee'] is Map<String, dynamic>) {
        final employee = result['employee'] as Map<String, dynamic>;
        final similarity = (result['similarity'] as num?)?.toDouble() ?? 0.0;

        setState(() {
          _status = 'Registrando ${widget.tipo}...';
        });
        await ApiService.registerLog(
          employee['emp_id'] as String? ?? '',
          widget.tipo,
          similarity,
        );

        if (!mounted) {
          return;
        }

        final now = TimeOfDay.now().format(context);
        _showSnack(
            '✅ ${widget.tipo == 'entrada' ? 'Entrada' : 'Saída'} registrada — ${employee['name']} — $now');
        await Future<void>.delayed(const Duration(seconds: 2));
        if (!mounted) {
          return;
        }
        Navigator.of(context).pop();
      } else {
        _showSnack('❌ Funcionário não reconhecido');
        setState(() {
          _status = 'Funcionário não reconhecido.';
          _processing = false;
        });
      }
    } catch (error) {
      _showSnack('❌ Erro: $error');
      setState(() {
        _status = 'Erro ao processar reconhecimento.';
        _processing = false;
      });
    }
  }

  void _showSnack(String message) {
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    _faceService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final title =
        widget.tipo == 'entrada' ? 'Registrar Entrada' : 'Registrar Saída';

    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  color: Colors.black,
                  width: double.infinity,
                  child: _loading
                      ? const Center(child: CircularProgressIndicator())
                      : (_controller != null &&
                              _controller!.value.isInitialized)
                          ? CameraPreview(_controller!)
                          : const Center(
                              child: Text(
                                'Câmera indisponível',
                                style: TextStyle(color: Colors.white),
                              ),
                            ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _status,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed:
                    _processing || _loading ? null : _captureAndRecognize,
                icon: _processing
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.face_retouching_natural),
                label: Text(
                    _processing ? 'Processando...' : 'Capturar e Reconhecer'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
