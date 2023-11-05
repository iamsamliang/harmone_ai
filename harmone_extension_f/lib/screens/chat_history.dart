import 'package:flutter/material.dart';
import '../providers/url.dart';
import 'package:provider/provider.dart';


class ChatHistoryPage extends StatefulWidget {
  const ChatHistoryPage({super.key});

  @override
  State<ChatHistoryPage> createState() => _ChatHistoryPageState();
}

class _ChatHistoryPageState extends State<ChatHistoryPage> {


  

  @override
  Widget build(BuildContext context) {

  final urlProvider = Provider.of<Url>(context);
  final currentUrl = urlProvider.url;


    return Scaffold(
      appBar: AppBar(
        title: Text(
          currentUrl,
          style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold),
          textAlign: TextAlign.center,
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF83a4d4), Color(0xFFb6fbff)],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: <Widget>[
              Expanded(
                child: ListView(
                  children: const <Widget>[
                    ChatBubble(
                      text: 'Hello, how was your day',
                      isUser: false,
                    ),
                    ChatBubble(
                      text: 'good, we are watching a lex fridman podcast today',
                      isUser: true,
                    ),
                    ChatBubble(
                      text: 'great!',
                      isUser: false,
                    ),
                    ChatBubble(
                      text: 'wow that was a good take by Marc Andreessen',
                      isUser: false,
                    ),
                    ChatBubble(
                      text: 'I know, right',
                      isUser: true,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;
  const ChatBubble({required this.text, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isUser ? Colors.blueAccent : Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: TextStyle(color: isUser ? Colors.white : Colors.black),
      ),
    );
  }
}
