import 'dart:async';
import 'dart:html';
import 'dart:js';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'dart:js_util' as js_util;
import 'dart:js' as js;
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import 'dart:convert';
import 'package:uuid/uuid.dart';
import 'package:harmone_extension_f/providers/chrome_api.dart' as chrome_api;
import 'package:harmone_extension_f/providers/url.dart';

class AudioRecord with ChangeNotifier {
  Timer? _silenceTimer;
  Timer? _recordingTimer;
  String pathToAudio = '/Users/luluchi/Downloads';
  FlutterSoundRecorder _recordingSession = FlutterSoundRecorder();
  
  double minVolume = -45.0;
  late StreamSubscription _recorderSubscription;
  bool isRecording = false;
  late var file; 
  String ytTimestamp = "0"; // update yt timestamp whenever start recording
  late String ytUrl;

  Future<void> initRecorder() async {
    await _recordingSession.openRecorder();
    _recordingSession.setSubscriptionDuration(const Duration(milliseconds: 500));
  }

  void startListening() async {
    await initRecorder();
    
    window.navigator.getUserMedia(audio: true).then((stream) async {
      startRecording();

      _recorderSubscription = _recordingSession.onProgress!.listen((e) {
        double? decibels = e.decibels;
        print("decibels");
        print(decibels);
        decibels = 60;
        if (decibels! > minVolume) {
          if (!isRecording) {
            startRecording();
          } 
        } else {
          _resetSilenceTimer();
        }  
      },);
    });
  }

  Future<void> startRecording() async {
    print("start recording");
    ytTimestamp = getCurrentYoutubeTimestamp();
    ytUrl = getCurrentTabUrl() as String;

    if(!isRecording) {
      isRecording = true;
      await _recordingSession.startRecorder(
        toFile: pathToAudio,
        // codec: Codec.pcm16WAV,
      );
    }
   
    // iterate on this later to pause recording every 60 seconds 
 
    // _recordingTimer?.cancel();
    // _recordingTimer = Timer.periodic(Duration(seconds: 60), (timer) {
    //   if (isRecording) {
    //     stopRecording();
    //     startRecording();
    //   }
    // });
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
    file = _recordingSession.stopRecorder();
    print("file");
    print(file);
    isRecording = false;
    _silenceTimer?.cancel();

    // upload the newly recorded audio file
    createPostRequest(ytUrl, file);
  }

  Future<http.Response> createPostRequest(String ytUrl, File audio_files) async {
    // TODO
    // need to confirm with pufeng what is the destination url
    var clientId = generateClientId();
    var updatedYtUrl = "/api/youtube/$ytUrl?client_id=$clientId";
    var destination_url = "/api/youtube/sayToAI?client_id=$clientId";

    var data = {
      "ytUrl": updatedYtUrl,
      "timestamp": ytTimestamp,
      "audio_files": audio_files,
    };
    
    return await http.post(
      Uri.parse(destination_url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(data),
    );
  }

  String generateClientId() {
    var uuid = const Uuid();
    String clientId = uuid.v4(); // Generates a unique ID

    return clientId;
  }

  dynamic getCurrentYoutubeTimestamp() async {
    print("calling getCurrentYoutubeTimestamp");
    var timestamp = "0";

    var sendMessage =
        js_util.getProperty(js.context['chrome']['runtime'], 'sendMessage');
    var response =
        await js_util.promiseToFuture(js_util.callMethod(sendMessage, [], [
      {
        'action': 'getYoutubeVideoCurrentTime',
      },
      js.allowInterop((result) {
        timestamp = result;
        print('Current video time: $result');
      })
    ]));

    return timestamp;
  }

  Future<String> getCurrentTabUrl() async {
    try {
      List<chrome_api.Tab> tabs = await js_util.promiseToFuture(
        chrome_api.query(chrome_api.ParameterQueryTabs(
            active: true, lastFocusedWindow: true)),
      );
      if (tabs.isNotEmpty && tabs.first.url.isNotEmpty) {
        ytUrl = tabs.first.url;
        Provider.of<Url>(context as BuildContext, listen: false).updateURL(ytUrl);
        print('Current tab URL: ${ytUrl}');
        return ytUrl;
      } else {
        throw Exception('No tabs found');
      }
    } catch (e) {
      throw Exception('Failed to get current tab URL: $e');
    }
  }
}
