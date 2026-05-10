int sensorPin = A0;

void setup () {
  Serial.begin(9600); 
  pinMode(13,OUTPUT); 
  pinMode(8,OUTPUT);
}

void loop() {
  int value = analogRead(sensorPin);
  Serial.println(value);

  // --- Приём команд (только если что-то пришло) ---
  if (Serial.available()) {                    // ← проверяем, есть ли данные
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "1") {
      digitalWrite(13, HIGH);
    } else if (command == "0") {
      digitalWrite(13, LOW);
    } else if (command =="buzz") {
      digitalWrite(8,HIGH);
      delay(300);
      digitalWrite(8,LOW);
    }
    
  }
  
  delay(1000);
}