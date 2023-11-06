import 'package:flutter/material.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:provider/provider.dart';
import 'dart:js_util';
import 'package:harmone_extension_f/providers/chrome_api.dart' as chrome_api;

class IntroPage extends StatefulWidget {
  const IntroPage({super.key});

  @override
  State<IntroPage> createState() => _IntroPageState();
}

class _IntroPageState extends State<IntroPage> {
  Future<void> _getCurrentTabUrl() async {
    try {
      List<chrome_api.Tab> tabs = await promiseToFuture(
        chrome_api.query(chrome_api.ParameterQueryTabs(
            active: true, lastFocusedWindow: true)),
      );
      if (tabs.isNotEmpty && tabs.first.url.isNotEmpty) {
        Provider.of<Url>(context, listen: false).updateURL(tabs.first.url);
        print('Current tab URL: ${tabs.first.url}');
      }
      else {
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
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              const Text(
                'Meet Jessica, she is excited to meet you and watch this YouTube video with you',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  // Fetch the current tab URL before navigating
                  await _getCurrentTabUrl();
                  // Navigate to ChatHistoryPage
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
