import 'dart:convert';
import 'package:http/http.dart' as http;


class Upload {
  Future<http.Response> createPost(String url, Map<String, dynamic> data) async {
    return await http.post(
      Uri.parse(url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(data),
    );
  }
}