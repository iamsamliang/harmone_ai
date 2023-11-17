import 'package:flutter/material.dart';
// import 'package:firebase_storage/firebase_storage.dart';

class Url with ChangeNotifier {
  String _url = '';

  String get url => _url;

  void updateURL(String newURL) {
    _url = newURL;
    notifyListeners();
  }
}