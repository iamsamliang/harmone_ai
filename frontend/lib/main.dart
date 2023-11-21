import 'package:flutter/material.dart';
import 'package:harmone_extension_f/providers/audio_record.dart';
import 'package:harmone_extension_f/screens/chat_history.dart';
import 'package:harmone_extension_f/providers/url.dart';
import 'package:provider/provider.dart';
import 'dart:html' as html;


import 'screens/welcome.dart';

void main() async {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => Url()),
        ChangeNotifierProvider(create: (context) => AudioRecord(),)
      ],
      child: MyApp(),
    ),);
}



class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Harmone AI',
      theme: ThemeData(
        // colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const WelcomePage(),
    );
  }
}

