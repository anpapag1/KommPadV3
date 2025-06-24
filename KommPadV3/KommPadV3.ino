#include <Keypad.h>

// Rotary encoder pins
#define encPin1 10
#define encPin2 16
#define SW 14

// Keypad configuration
#define numRows 2  // Number of rows in the keypad
#define numCols 3  // Number of columns in the keypad
char keymap[numRows][numCols] = { { '1', '2', '3' },
                                  { '4', '5', '6' } };

// Define the row and column pins connected to the keypad
byte colPins[numCols] = { 6, 7, 8 };  // Columns 1 to 3
byte rowPins[numRows] = { 5, 4 };     // Rows 1 to 2

// Create a Keypad object
Keypad keypad = Keypad(makeKeymap(keymap), rowPins, colPins, numRows, numCols);

// Encoder state variables
int currentStateencPin1;
int lastStateencPin1;

const uint8_t MAX_LAYERS = 4;   // 0 … 3   (adjust if you need more)
volatile uint8_t currentLayer = 0;

// Setup function to initialize components
void setup() {

  Serial.begin(9600);
  Serial.println("KommPad starting...");
  
  // Set pin modes for encoder and switch
  pinMode(encPin1, INPUT_PULLUP);
  pinMode(encPin2, INPUT_PULLUP);
  pinMode(SW, INPUT_PULLUP);

  // Initialize encoder state
  lastStateencPin1 = digitalRead(encPin1);  // Encoder 1 initial state
}

void loop() {
  read_serial();
  read_btn();
  read_enc();


  delay(1);  // Small delay to ensure the loop runs smoothly
}

void read_btn() {
  // Get pressed key from the keypad
  char key = keypad.getKey();

  // If a key is pressed, execute the corresponding action
  if (key != NO_KEY) {
    sendEvent(key);
  }
}

void read_enc() {
  currentStateencPin1 = digitalRead(encPin1);                                 // Read the current state of the encoder pin
  if (currentStateencPin1 != lastStateencPin1 && currentStateencPin1 == 1) {  // Encoder pin change detection
    if (digitalRead(encPin2) != currentStateencPin1) {                        // Counter-clockwise rotation
      sendEvent('7');
    } else {  // Clockwise rotation
      sendEvent('8');
    }
  }
  lastStateencPin1 = currentStateencPin1;  // Store the last encoder pin state

  // Check if encoder switch (SW) is pressed
  if (digitalRead(SW) == LOW) {
    currentLayer = (currentLayer + 1) % MAX_LAYERS;
    while (digitalRead(SW) == LOW) {}  // Wait for switch release or long press time
  }
}

void read_serial() {
  // Check if data is available on the serial port
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  // Read input until newline
    input.trim();  // Remove leading and trailing whitespace

    // Process the input command
    if (input == "ping") {
      Serial.println("KommPong");
    } else if (input == "leyerUp") {
      currentLayer = (currentLayer + 1) % MAX_LAYERS;
      Serial.print("Layer changed to: ");
      Serial.println(currentLayer);
    } else {
      Serial.print("Unknown command: ");
      Serial.println(input);
    }
  }
}

void sendEvent(char btn) {
  Serial.print(F("button"));
  Serial.print(btn);              // 0…5
  Serial.print(F(" layer"));
  Serial.println(currentLayer);   // 0…MAX_LAYERS-1
}
