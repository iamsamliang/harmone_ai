import 'dart:async';
import 'dart:html';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';

class AudioRecord with ChangeNotifier {
  Timer? _silenceTimer;
  Timer? _recordingTimer;

  String pathToAudio = '/Users/luluchi/Downloads';
  FlutterSoundRecorder _recordingSession = FlutterSoundRecorder();
  
  double minVolume = -45.0;
  late String recordFilePath;
  late StreamSubscription _recorderSubscription;
  bool isRecording = false;
  late List files; 

  Future<void> initRecorder() async {
    await _recordingSession.openRecorder();
    _recordingSession.setSubscriptionDuration(const Duration(milliseconds: 500));
  }

  void startListening() async {
    await initRecorder();
    
    //  PermissionStatus status = await Permission.microphone.request();
    // // bool hasPermission = await _recordingSession.hasPermission();
    monitorAudioLevel();
  }

  Future<void> startRecording() async {
    print("start recording");

    await _recordingSession.startRecorder(
      toFile: pathToAudio,
      // codec: Codec.pcm16WAV,
    );
  
    _recordingTimer?.cancel();
    _recordingTimer = Timer.periodic(Duration(seconds: 60), (timer) {
      if (isRecording) {
        stopRecording();
        startRecording();
      } else {
        isRecording = true;
      }   
    });
  }

  Future<void> stopRecording() async {
    print("stop recording");
    var file = _recordingSession.stopRecorder();
    isRecording = false;
    _silenceTimer?.cancel();
  }

  void monitorAudioLevel() {
    print("monitorAudioLevel");
    window.navigator.getUserMedia(audio: true).then((stream) => {
      _recorderSubscription =
        _recordingSession.onProgress!.listen((e) {
        double? decibels = e.decibels;
        decibels = 60;
        print("decibels");
        print(decibels);
        if (decibels! > minVolume) {
          if (!isRecording) {
            startRecording();
          }
          _silenceTimer?.cancel();
        } else {
          _silenceTimer = Timer(Duration(seconds: 1), () {
            if (isRecording) {
              stopRecording();
            }
          });
        }  
      })
    });
  }
}