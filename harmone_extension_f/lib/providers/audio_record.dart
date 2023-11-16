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
    
    window.navigator.getUserMedia(audio: true).then((stream) async {
      await _recordingSession.startRecorder(
        toFile: pathToAudio,
        // codec: Codec.pcm16WAV,
      );
      isRecording = true;

      _recorderSubscription = _recordingSession.onProgress!.listen((e) {
        double? decibels = e.decibels;
        print("decibels");
        print(decibels);
        decibels = 60;
        if (decibels! > minVolume) {
          if (!isRecording) {
            startRecording();
          }
          _resetSilenceTimer();
        } else {
          _silenceTimer = Timer(Duration(seconds: 1), () {
            if (isRecording) {
              stopRecording();
            }
          });
        }  
      }, onError: (error) {
        print('Error in stream: $error');
      },
      );
    });
  }

  Future<void> startRecording() async {
    print("start recording");
    if(!isRecording) {
      isRecording = true;
      await _recordingSession.startRecorder(
        toFile: pathToAudio,
        // codec: Codec.pcm16WAV,
      );
    }
   
    _recordingTimer?.cancel();
    _recordingTimer = Timer.periodic(Duration(seconds: 60), (timer) {
      if (isRecording) {
        stopRecording();
        startRecording();
      }
    });
  }

  void _resetSilenceTimer() {
    _silenceTimer?.cancel();
    _silenceTimer = Timer(const Duration(seconds: 1), () {
      if (isRecording) {
        stopRecording();
      }
    });
  }

  Future<void> stopRecording() async {
    print("stop recording");
    var file = _recordingSession.stopRecorder();
    print("file");
    print(file);
    isRecording = false;
    _silenceTimer?.cancel();
  }
}
