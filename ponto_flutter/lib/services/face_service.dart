import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:image/image.dart' as img;
import 'package:permission_handler/permission_handler.dart';

class FaceCaptureResult {
  final bool faceDetected;
  final String? imageBase64;

  FaceCaptureResult({required this.faceDetected, required this.imageBase64});
}

class FaceService {
  final FaceDetector _faceDetector = FaceDetector(
    options: FaceDetectorOptions(
      enableClassification: false,
      enableContours: false,
      performanceMode: FaceDetectorMode.fast,
    ),
  );

  Future<bool> ensureCameraPermission() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<List<CameraDescription>> loadCameras() {
    return availableCameras();
  }

  Future<FaceCaptureResult> captureFaceBase64(XFile file) async {
    final bytes = await file.readAsBytes();
    final inputImage = InputImage.fromFilePath(file.path);
    final faces = await _faceDetector.processImage(inputImage);

    if (faces.isEmpty) {
      return FaceCaptureResult(faceDetected: false, imageBase64: null);
    }

    final base64Image = _normalizeImage(bytes);
    return FaceCaptureResult(faceDetected: true, imageBase64: base64Image);
  }

  String _normalizeImage(Uint8List bytes) {
    final decoded = img.decodeImage(bytes);
    if (decoded == null) {
      return base64Encode(bytes);
    }

    final jpg = img.encodeJpg(decoded, quality: 88);
    return base64Encode(jpg);
  }

  Future<void> dispose() async {
    await _faceDetector.close();
  }
}
