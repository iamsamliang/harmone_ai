

import 'dart:async';
import 'package:flutter_sound/flutter_sound.dart';

class AudioRecord {
  Timer? timer1;
  Timer? timer2;
  String pathToAudio = '/Users/luluchi/Downloads';
  late FlutterSoundRecorder _recordingSession;
  double minVolume = -45.0;
  bool isRecording = false;
  late String recordFilePath;
  late StreamSubscription _recorderSubscription;
  int noTalkDuration = 0;
  double currentVolume = -100; // temporary
  bool noTalkingDuration1s = false; 
  // AudioRecorder myRecording = AudioRecorder();
  late Record audioRecord;

  // startTimer() will repeat a function call to updateVolume() to retrieve microphone data every 10 milliseconds. 
  startTimerToDetectTalking() async {
    timer1 ??= Timer.periodic(
        const Duration(milliseconds: 1000), (timer) => detectTalking());
  }

  // > 1 second is determined as not talking
  startTimerToDetectNotTalking() async {
    timer2 ??= Timer.periodic(
        const Duration(milliseconds: 100), (timer) => detectNotTalking());
  }

  detectNotTalking() async {
    // currentVolume = ???
    if (currentVolume < minVolume) {
      noTalkDuration++;
      print(noTalkDuration);
    } else {
      noTalkDuration = 0;
    }

    if (noTalkDuration > 10) {
      print("noTalkingDuration1s true");
      timer2?.cancel();
      setState(() {
        noTalkingDuration1s = true;
      });
    }
  }

  detectTalking() async {
    bool shouldRecord = false;
    
    shouldRecord = true; // temporary
    // shouldRecord = ampl.current > minVolume;
    if (shouldRecord) {
      timer1?.cancel();
      // await Start();
      startRecording();
    }
  }

  Future<void> startRecording() {

  }
}