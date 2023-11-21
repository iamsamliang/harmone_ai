import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_sound/public/flutter_sound_recorder.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:harmone_extension_f/providers/audio_record.dart';
import 'package:provider/provider.dart';
import 'dart:js_util' as js_util;
import 'dart:js' as js;


class IntroPage extends StatefulWidget {
  const IntroPage({super.key});

  @override
  State<IntroPage> createState() => _IntroPageState();
}

class _IntroPageState extends State<IntroPage> {

  void sendMessageToContentScript() async {
    var sendMessage =
        js_util.getProperty(js.context['chrome']['runtime'], 'sendMessage');
    var response =
        await js_util.promiseToFuture(js_util.callMethod(sendMessage, [], [
      'your-extension-id', // Replace with your actual extension ID
      {'action': 'testMessage', 'payload': 'Hello from Dart!'},
      js.allowInterop((result) {
        print('Response from content script: $result');
      })
    ]));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF83a4d4), Color(0xFFb6fbff)],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                const Text(
                  'Meet Jessica, she is excited to meet you and watch this YouTube video with you!',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    shadows: [
                      Shadow(
                        offset: Offset(2.0, 2.0),
                        blurRadius: 3.0,
                        color: Color.fromARGB(150, 0, 0, 0),
                      ),
                    ],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32), // Increased spacing
                Material(
                  elevation: 5.0, // Add shadow to the button
                  borderRadius: BorderRadius.circular(30.0), // Rounded corners
                  child: Container(
                    width: double.infinity, // Make the button wider
                    height: 60, // Increase button height
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(30.0),
                    ),
                    child: ElevatedButton(
                      onPressed: () async {
                        sendMessageToContentScript();
                        String url =
                            // await getCurrentTabUrl(); 
                            Provider.of<AudioRecord>(context as BuildContext, listen: false).getCurrentTabUrl() as String; // Fetch the current tab URL
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => const ChatHistoryPage(),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        primary: Colors.white, // Background color
                        onPrimary: const Color(0xFF83a4d4), // Text color
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30.0),
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [  
                          ElevatedButton.icon(
                            onPressed: () async {
                              Provider.of<AudioRecord>(context, listen: false).startListening();
                            },
                            label: const Text(
                              'Start Session',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF83a4d4),
                              ),
                            ), icon: const Icon(
                              Icons.play_circle_fill,
                              color: Color(0xFF83a4d4),
                            ),
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
