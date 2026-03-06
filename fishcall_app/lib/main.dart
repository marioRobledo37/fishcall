import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'api.dart';

void main() {
  runApp(FishCallApp());
}

class FishCallApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FishCall',
      home: CapturePage(),
    );
  }
}

class CapturePage extends StatefulWidget {
  @override
  _CapturePageState createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {

  final numberController = TextEditingController();
  final lengthController = TextEditingController();

  String species = "Dorado";
  bool enviando = false;

  final ImagePicker picker = ImagePicker();
  File? photo;

  Future tomarFoto() async {

    final XFile? image = await picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 70,
    );

    if (image != null) {
      setState(() {
        photo = File(image.path);
      });
    }

  }

  void enviar() async {

    if (enviando) return;

    setState(() {
      enviando = true;
    });

    await enviarCaptura(
      numberController.text,
      species,
      lengthController.text,
      photo
    );

    numberController.clear();
    lengthController.clear();

    setState(() {
      species = "Dorado";
      enviando = false;
      photo = null;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Captura registrada")),
    );
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: Text("Registrar captura"),
      ),

      body: Padding(
        padding: EdgeInsets.all(20),

        child: SingleChildScrollView(
          child: Column(
            children: [

              TextField(
                controller: numberController,
                decoration: InputDecoration(
                  labelText: "Número de pescador",
                ),
                keyboardType: TextInputType.number,
              ),

              SizedBox(height: 20),

              DropdownButton<String>(
                value: species,
                isExpanded: true,
                items: [
                  "Dorado",
                  "Surubí",
                  "Boga",
                  "Pacú"
                ].map((s) {

                  return DropdownMenuItem(
                    value: s,
                    child: Text(s),
                  );

                }).toList(),
                onChanged: (value) {
                  setState(() {
                    species = value!;
                  });
                },
              ),

              SizedBox(height: 20),

              TextField(
                controller: lengthController,
                decoration: InputDecoration(
                  labelText: "Medida (cm)",
                ),
                keyboardType: TextInputType.number,
              ),

              SizedBox(height: 20),

              ElevatedButton(
                onPressed: tomarFoto,
                child: Text("TOMAR FOTO"),
              ),

              SizedBox(height: 20),

              photo != null
                  ? Image.file(photo!, height: 200)
                  : Text("Sin foto"),

              SizedBox(height: 30),

              ElevatedButton(
                onPressed: enviando ? null : enviar,
                child: enviando
                    ? SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : Text("ENVIAR CAPTURA"),
              ),

            ],
          ),
        ),
      ),
    );
  }
}