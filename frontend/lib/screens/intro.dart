import 'dart:async';
import 'dart:io';
import 'package:harmone_extension_f/providers/chrome_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_sound/public/flutter_sound_recorder.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:harmone_extension_f/providers/audio_record.dart';
import 'package:harmone_extension_f/providers/chrome_api.dart' as chrome_api;
import 'package:provider/provider.dart';
import 'dart:js_util' as js_util;
import 'dart:js' as js;
import 'package:chrome_extension/storage.dart';

class IntroPage extends StatefulWidget {
  const IntroPage({super.key});

  @override
  State<IntroPage> createState() => _IntroPageState();
}

class _IntroPageState extends State<IntroPage> {
  // void sendMessageToContentScript() async {
  //   var sendMessage =
  //       js_util.getProperty(js.context['chrome']['runtime'], 'sendMessage');
  //   var response =
  //       await js_util.promiseToFuture(js_util.callMethod(sendMessage, [], [
  //     'your-extension-id', // Replace with your actual extension ID
  //     {'action': 'testMessage', 'payload': 'Hello from Dart!'},
  //     js.allowInterop((result) {
  //       print('Response from content script: $result');
  //     })
  //   ]));
  // }

  Future<dynamic> _fetchCurrentTimeFromLocalStorage() async {
    try {
      await Future.delayed(
          const Duration(milliseconds: 5)); // Introduce a delay
      var values = await chrome.storage.local.get(null /* all */);
      return values['currentTime'];
    } catch (e) {
      print('Error fetching current time: $e');
      return null;
    }
  }

  Future<String> _getCurrentTabUrl() async {
    try {
      List<chrome_api.Tab> tabs = await js_util.promiseToFuture(
        chrome_api.query(chrome_api.ParameterQueryTabs(
            active: true, lastFocusedWindow: true)),
      );
      if (tabs.isNotEmpty && tabs.first.url.isNotEmpty) {
        var ytUrl = tabs.first.url;
        Provider.of<Url>(context, listen: false).updateURL(ytUrl);
        print('Current tab URL: ${ytUrl}');
        return ytUrl;
      } else {
        throw Exception('No tabs found');
      }
    } catch (e) {
      throw Exception('Failed to get current tab URL: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF232526),
              Color(0xFF414345)
            ], // Updated dark gradient
          ),
        ),
        child: Padding(
          padding:
              const EdgeInsets.symmetric(horizontal: 36.0), // Increased padding
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                const Text(
                  'Lebron is waiting for you!',
                  style: TextStyle(
                    fontFamily: 'Montserrat', // Consistent font family
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    shadows: [
                      Shadow(
                        offset: Offset(3.0, 3.0), // Slightly larger shadow
                        blurRadius: 4.0,
                        color: Color.fromARGB(180, 0, 0, 0),
                      ),
                    ],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 28),
                Material(
                  elevation:
                      10.0, // Enhanced shadow for a more pronounced effect
                  borderRadius: BorderRadius.circular(30.0),
                  child: Container(
                    width: double.infinity,
                    height: 60,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(30.0),
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Color(0xFF646F80),
                          Color(0xFF28313B)
                        ], // Button gradient
                      ),
                    ),
                    child: ElevatedButton(
                      onPressed: () async {
                        sendMessage(ParameterSendMessage(
                            type: "record", data: "start"));
                        // String url = await _getCurrentTabUrl();
                        // var values = await _fetchCurrentTimeFromLocalStorage();
                        // print("from flutter, current time: $values");
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const ChatHistoryPage(),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        primary: Colors.transparent, // Transparent background
                        shadowColor:
                            Colors.transparent, // No shadow for the button
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30.0),
                        ),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Start Recording',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white, // Updated text color
                            ),
                          ),
                          SizedBox(width: 10),
                          Icon(
                            Icons.play_circle_fill,
                            color: Colors.white, // Updated icon color
                          ),
                        ],
                      ),
                    ),
                  ),
                ), // Increased spacing for a cleaner look
                const SizedBox(height: 28),
                Material(
                  elevation:
                      10.0, // Enhanced shadow for a more pronounced effect
                  borderRadius: BorderRadius.circular(30.0),
                  child: Container(
                    width: double.infinity,
                    height: 60,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(30.0),
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Color(0xFF646F80),
                          Color(0xFF28313B)
                        ], // Button gradient
                      ),
                    ),
                    child: ElevatedButton(
                      onPressed: () async {
                        sendMessage(ParameterSendMessage(
                            type: "counter", data: "hello"));
                        String url = await _getCurrentTabUrl();
                        // Provider.of<AudioRecord>(context as BuildContext,
                        //             listen: false)
                        //         .getCurrentTabUrl()
                        //     as String; // Fetch the current tab URL
                        var values = await _fetchCurrentTimeFromLocalStorage();
                        print("from flutter, current time: $values");
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const ChatHistoryPage(),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        primary: Colors.transparent, // Transparent background
                        shadowColor:
                            Colors.transparent, // No shadow for the button
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30.0),
                        ),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Start Session',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white, // Updated text color
                            ),
                          ),
                          SizedBox(width: 10),
                          Icon(
                            Icons.play_circle_fill,
                            color: Colors.white, // Updated icon color
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
