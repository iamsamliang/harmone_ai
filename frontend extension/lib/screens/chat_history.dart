import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../providers/url.dart';
import 'package:provider/provider.dart';

class GradientAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final double height;

  const GradientAppBar({
    required this.title,
    this.height = kToolbarHeight,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF83a4d4), Color(0xFFb6fbff)],
        ),
      ),
      child: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        centerTitle: true,
        title: Text(
          title,
          style: const TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.bold,
            color: Colors.black,
          ),
        ),
      ),
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(height);
}

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
      extendBodyBehindAppBar: true, // Extend the body behind the app bar
      appBar: const GradientAppBar(
          title: "Chat History"), // Custom gradient app bar
      body: Container(
        padding: const EdgeInsets.only(top: kToolbarHeight + 20),
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF83a4d4), Color(0xFFb6fbff)],
          ),
        ),
        child: const Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            children: <Widget>[
              ChatBubble(
                text: 'Hello, how was your day',
                isUser: false,
              ),
              ChatBubble(
                text: 'Good, we are watching a lex fridman podcast today',
                isUser: true,
              ),
              ChatBubble(
                text: 'Great!',
                isUser: false,
              ),
              ChatBubble(
                text: 'Wow that was a good take by Marc Andreessen!',
                isUser: false,
              ),
              ChatBubble(
                text: 'Absolutely!',
                isUser: true,
              ), // ... Your existing ListView of ChatBubbles
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
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 10),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isUser ? Colors.blueAccent : Colors.white,
          borderRadius: isUser
              ? const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  bottomLeft: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                )
              : const BorderRadius.only(
                  topRight: Radius.circular(16),
                  bottomLeft: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              spreadRadius: 2,
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Text(
          text,
          style: TextStyle(color: isUser ? Colors.white : Colors.black),
        ),
      ),
    );
  }
}
