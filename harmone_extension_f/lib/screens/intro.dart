import 'package:flutter/material.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:provider/provider.dart';
import 'dart:js_util' as js_util;
import 'package:harmone_extension_f/providers/chrome_api.dart' as chrome_api;
import 'dart:js' as js;

class IntroPage extends StatefulWidget {
  const IntroPage({super.key});

  @override
  State<IntroPage> createState() => _IntroPageState();
}

class _IntroPageState extends State<IntroPage> {

  void getCurrentYoutubeTimestamp() async {
    print("calling getCurrentYoutubeTimestamp");
    try {
      var sendMessage =
          js_util.getProperty(js.context['chrome']['runtime'], 'sendMessage');
      var response =
          await js_util.promiseToFuture(js_util.callMethod(sendMessage, [], [
        {
          'action': 'getYoutubeVideoCurrentTime',
        },
        js.allowInterop((result) {
          print('Current video time: $result');
        })
      ]));
    } catch (e) {
      print('Error sending message: $e');
    }
  }

  Future<void> _getCurrentTabUrl() async {
    try {
      List<chrome_api.Tab> tabs = await js_util.promiseToFuture(
        chrome_api.query(chrome_api.ParameterQueryTabs(
            active: true, lastFocusedWindow: true)),
      );
      if (tabs.isNotEmpty && tabs.first.url.isNotEmpty) {
        Provider.of<Url>(context, listen: false).updateURL(tabs.first.url);
        print('Current tab URL: ${tabs.first.url}');
      } else {
        print('No tabs found');
      }
    } catch (e) {
      print('Failed to get current tab URL: $e');
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
                        getCurrentYoutubeTimestamp();
                        await _getCurrentTabUrl(); // Fetch the current tab URL
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
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            'Start Session',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF83a4d4),
                            ),
                          ),
                          SizedBox(width: 10),
                          Icon(
                            Icons.play_circle_fill,
                            color: Color(0xFF83a4d4),
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
