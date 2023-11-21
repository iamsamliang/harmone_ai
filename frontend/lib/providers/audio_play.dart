import 'package:just_audio/just_audio.dart' as just_audio;
import 'package:collection/collection.dart';

class AudioPlay {
  PriorityQueue<List<dynamic>> queue = PriorityQueue<List<dynamic>>(
    (a, b) => a[0].compareTo(b[0]) // compare the timestamp of the video
  );
  var audioPlayer = just_audio.AudioPlayer();

  // play audio in the conversation with user
  Future<void> playAudio(int timestamp, String url) async {
    // await audioPlayer.setUrl('http://techslides.com/demos/samples/sample.mp3'); 
    await audioPlayer.setUrl(url);                
    audioPlayer.play();    
  }

  // play audio response to the YT video highlights
  Future<void> playAudioSequentially() async {
    // play the top one in the pq
    List<dynamic> firstVideo = queue.removeFirst();
    await audioPlayer.setUrl(firstVideo[1]);
  }

  addToPlayList(int timestamp, String url) {
    queue.add([timestamp, url]);
  }

}