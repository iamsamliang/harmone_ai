import 'package:flutter/material.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:js/js.dart';
import 'package:provider/provider.dart';
import 'dart:js' as js;


@JS('chrome.runtime.sendMessage')
external void sendMessage(Object message, void Function(String) responseCallback);

void requestCurrentTabUrl(BuildContext context) {
  js.context.callMethod('sendMessageToBackground', [
    {'message': 'get_url'},
    (String url) {
      print('Current tab URL: $url');
      Provider.of<Url>(context, listen: false).updateURL(url);
    },
  ]);
}

class IntroPage extends StatefulWidget {
  const IntroPage({super.key});

  @override
  State<IntroPage> createState() => _IntroPageState();
}

class _IntroPageState extends State<IntroPage> {
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
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              const Text(
                'Meet Jessica, she is excited to meet you and watch this YouTube video with you',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign:
                    TextAlign.center, // Centers the text within the Text widget
              ),
              const SizedBox(
                  height: 20), // Adds spacing between the text and button
              ElevatedButton(
                onPressed: () {
                  // requestCurrentTabUrl(
                  //     context); // pass context to requestCurrentTabUrl
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (context) => const ChatHistoryPage(),
                    ),
                  );
                },
                child: const Text('Start Session'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
