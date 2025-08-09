#include <Keypad.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_NeoPixel.h>
//#include <sstream> // Include sstream for istringstream

// OLED configuration
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(128, 32, &Wire, -1);

#define PIN 15
#define NUM_LEDS 2  // Change to the number of LEDs you have
Adafruit_NeoPixel strip(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);
int num_Colors;  // Variable to store the count of non-empty colors
String Colors[4];
uint8_t brightness;
String effect;
float breathBrightness = 1.0;     // Variable for breathing effect brightness

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

// Variables
uint8_t MAX_LAYERS = 4;   
volatile uint8_t currentLayer = 0;
String layerNames[4]; // Adjust size as needed
String display_names[4][6];
uint16_t idleTime;

int xPos[] = { 0, 48, 92 };  // X positions for the columns
int yPos[] = { 0, 25 };      // Y positions for the rows
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

  strip.begin();

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


  Led(effect);
  
  delay(1);
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
      sendEvent("encoder", '3');
    } else {  // Clockwise rotation
      sendEvent("encoder", '1');
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
        } else if (input.startsWith("DisplayNames:")) {  // Check if input is a display names string
            Serial.println("Display names received.");
            loadDisplayNames(input);  // Pass the display names string to loadDisplayNames
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
  display.setTextSize(2);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(30, 9);
  
  // Display layer name if available, otherwise show layer number
  if (currentLayer < 4 && layerNames[currentLayer].length() > 0) {
    display.println(layerNames[currentLayer]);
    if (1) {
      display.setTextSize(1);      // Set the text size for actions
      for (int row = 0; row < 2; row++) {
        for (int col = 0; col < 3; col++) {
          display.setCursor(xPos[col], yPos[row]);
          display.print(display_names[currentLayer][col+row*3]);  // Adjusted to access the correct action
        }
      }
    }
  } else {
    display.clearDisplay();
  }
  
  display.display();                  // Update the display
}

int splitString(String& input, char delimiter, String arr[]) {
  Serial.print("Splitting string: '");
  Serial.print(input);
  Serial.println("'");

    int index = 0;
    int inputLength = input.length();
    int start = 0;
    
    // Safety check
    if (inputLength == 0) {
        return 0;
    }
    
    // Find each delimiter and extract substrings
    for (int i = 0; i <= inputLength; i++) {
        // Check if we found a delimiter or reached the end of string
        if (i == inputLength || input.charAt(i) == delimiter) {
            // Extract substring from start to current position
            if (i > start) {
                arr[index] = input.substring(start, i);
            } else {
                arr[index] = "";  // Empty string for consecutive delimiters
            }
            
            // Debug output
            Serial.print("Token[");
            Serial.print(index);
            Serial.print("]: '");
            Serial.print(arr[index]);
            Serial.println("'");
            
            index++;
            start = i + 1;  // Start next token after the delimiter
            
            // Safety check to prevent array overflow
            if (index >= 50) {  // Adjust this limit as needed
                Serial.println("Warning: Maximum tokens reached!");
                break;
            }
        }
    }
    
    Serial.print("Total tokens found: ");
    Serial.println(index);
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
  int layerCount = splitString(settingList[1], '~', layerNames);
  updateDisplay();
  brightness = settingList[2].toInt();  // Set LED brightness from settings
  effect = settingList[3];  // Set effect from settings
  num_Colors = splitString(settingList[4], '~', Colors);
  idleTime = settingList[5].toInt();  // Set idle timeout from settings
  // Serial.println(splitString(settingList[6], '|', temp));
  // splitString(temp[0], '~', display_names[0]);
  // splitString(temp[1], '~', display_names[1]);
  // splitString(temp[2], '~', display_names[2]);
  // splitString(temp[3], '~', display_names[3]);
  // Print display names for debugging
}

void loadDisplayNames(String names_str) {
  Serial.println(names_str);
  names_str.remove(0, 14);  // Remove "DisplayNames:" prefix

  String nameLayers[4]; // Adjust size as needed

  // Use the splitString function to split the display names string by '|'
  splitString(names_str, '|', nameLayers);
  splitString(nameLayers[0], '~', display_names[0]);
  splitString(nameLayers[1], '~', display_names[1]);
  splitString(nameLayers[2], '~', display_names[2]);
  splitString(nameLayers[3], '~', display_names[3]);

  // Print the split display names for debugging
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 6; j++) {
      Serial.print("DisplayName[");
      Serial.print(i);
      Serial.print("][");
      Serial.print(j);
      Serial.print("]: ");
      Serial.println(display_names[i][j]);
    }
  }

}

void Led(String effect) {
  strip.clear(); 
  strip.setBrightness(map(brightness, 0, 100, 0, 255));  // Set brightness for the strip
  if (effect == "solid") {
    strip.fill(hex2strip(Colors[currentLayer % num_Colors]));
  }else if (effect == "breathing") {
    strip.fill(hex2strip(Colors[currentLayer % num_Colors]));
    breathBrightness -= 0.001; 
    strip.setBrightness(map(brightness, 0, 100, 0, 255) * abs(breathBrightness));
    if (breathBrightness <= -1.0) {
      breathBrightness = 1.0;  // Reset brightness to 1.0
    }

  } else if (effect == "rainbow") {
    
    }else{
    strip.clear();  // Clear the strip if no valid effect is set
  }
  strip.show();   
}

uint32_t hex2strip(String hexColor) {
  // Convert hex color string to RGB values
  long number = strtol(&hexColor[1], NULL, 16);  // Skip the '#' character
  uint8_t r = (number >> 16) & 0xFF;  // Extract red component
  uint8_t g = (number >> 8) & 0xFF;   // Extract green component
  uint8_t b = number & 0xFF;          // Extract blue component
  return strip.Color(r, g, b);       // Return the color in Adafruit format
}