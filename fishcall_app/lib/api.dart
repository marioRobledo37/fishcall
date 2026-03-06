import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

Future enviarCaptura(String number, String species, String length, File? photo) async {

  var uri = Uri.parse("http://192.168.0.3:8000/api/capture/");

  var request = http.MultipartRequest("POST", uri);

  request.fields["number"] = number;
  request.fields["species"] = species;
  request.fields["length_cm"] = length;

  if (photo != null) {
    request.files.add(
      await http.MultipartFile.fromPath(
        "photo",
        photo.path,
      ),
    );
  }

  var response = await request.send();

  if (response.statusCode == 200) {

    var respStr = await response.stream.bytesToString();
    print(respStr);

  } else {

    print("Error: ${response.statusCode}");

  }
}