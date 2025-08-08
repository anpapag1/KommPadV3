#include <Keypad.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
//#include <sstream> // Include sstream for istringstream

// OLED configuration
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(128, 32, &Wire, -1);

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

// LED pins
#define Leds 9

// Encoder state variables
int currentStateencPin1;
int lastStateencPin1;

// Variables
uint8_t MAX_LAYERS = 4;   
volatile uint8_t currentLayer = 0;

// Variables for LEDs (brightness, mode, colors)
uint16_t ledBrightness = 255;  // LED brightness (0-255)
uint8_t ledMode = 0;           // LED mode (0-3)
String Colors[4] = {};  // Example colors

// Setup function to initialize components
void setup() {
  Serial.begin(9600);
  Serial.println("KommPad starting...");
  
  // Initialize OLED display
// SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }  
  display.clearDisplay();
  display.display();

  // Set pin modes for encoder and switch
  pinMode(encPin1, INPUT_PULLUP);
  pinMode(encPin2, INPUT_PULLUP);
  pinMode(SW, INPUT_PULLUP);

  // Initialize encoder state
  lastStateencPin1 = digitalRead(encPin1);  // Encoder 1 initial state

  // Display initial layer
  updateDisplay();
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
    sendEvent("button", key);
  }
}

void read_enc() {
  currentStateencPin1 = digitalRead(encPin1);                                 // Read the current state of the encoder pin
  if (currentStateencPin1 != lastStateencPin1 && currentStateencPin1 == 1) {  // Encoder pin change detection
    if (digitalRead(encPin2) != currentStateencPin1) {                        // Counter-clockwise rotation
      sendEvent("encoder", '1');
    } else {  // Clockwise rotation
      sendEvent("encoder", '3');
    }
    updateDisplay(); // Update the OLED display after encoder rotation
  }
  lastStateencPin1 = currentStateencPin1;  // Store the last encoder pin state

  // Check if encoder switch (SW) is pressed
  if (digitalRead(SW) == LOW) {
    sendEvent("encoder", '2');
    while (digitalRead(SW) == LOW) {}  // Wait for switch release or long press time
    updateDisplay(); // Update the OLED display after switch press
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
        } else if (input == "layerUp") {
            currentLayer = (currentLayer + 1) % MAX_LAYERS;
            Serial.print("Layer changed to: ");
            Serial.println(currentLayer);
            updateDisplay(); // Update the OLED display after layer change
        } else if (input.startsWith("Settings:")) {  // Check if input is a settings string
            Serial.println("Settings received.");
            loadSettings(input);  // Pass the settings string to loadSettings
        } else {
            Serial.print("Unknown command: ");
            Serial.println(input);
        }
    }
}

void sendEvent(String prefix, char btn) {
  Serial.print(prefix);
  Serial.print(btn);              // 0…5
  Serial.print(F(" layer"));
  Serial.println(currentLayer);   // 0…MAX_LAYERS-1
}

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0, 0);            // Start at top-left corner
  display.print(F("Current Layer: "));
  display.println(currentLayer);      // Display the current layer
  display.display();                  // Update the display
}

int splitString(String& input, char delimiter, String arr[]) {
    int index = 0;
    int start = 0;
    int end = input.indexOf(delimiter);

    while (end != -1) {
        arr[index++] = input.substring(start, end);
        start = end + 1;
        end = input.indexOf(delimiter, start);
    }

    // Add the last token
    if (start < input.length()) {
        arr[index++] = input.substring(start);
    }
    return index;
}

void loadSettings(String settings) {
    
    Serial.println(settings);
    settings.remove(0, 10);  // Remove "Settings:" prefix

    String settingList[10]; // Adjust size as needed

    // Use the splitString function to split the settings string by ','
    int size = splitString(settings, ',', settingList);

    // Print the split settings for debugging
    for (int i = 0; i < size; i++) {
        Serial.print("Setting[");
        Serial.print(i);
        Serial.print("]: ");
        Serial.println(settingList[i]);
    }
    MAX_LAYERS = settingList[0].toInt();
    currentLayer = 0;
    
}