input string ZonesFilePath = "zones.json"; // Chemin du fichier JSON contenant les zones

void OnStart()
{
   string symbol = Symbol();  // Détecter la paire automatiquement
   int timeframe = Period();  // Détecter le timeframe automatiquement

   Print("Exécution du script pour la paire : ", symbol, " sur le timeframe : ", PeriodSeconds(timeframe) / 60, " minutes.");

   // Écrire les informations de la paire et du timeframe dans zones.json
   if (!WriteSymbolAndTimeframeToJson(symbol, timeframe))
   {
      Print("Erreur : Impossible de mettre à jour le fichier zones.json avec la paire et le timeframe.");
      return;
   }

   // Lire le contenu du fichier zones.json
   string jsonContent;
   int fileHandle = FileOpen(ZonesFilePath, FILE_READ | FILE_TXT);
   if (fileHandle == INVALID_HANDLE)
   {
      Print("Erreur : Impossible d'ouvrir le fichier des zones : ", ZonesFilePath);
      return;
   }
   jsonContent = FileReadString(fileHandle);
   FileClose(fileHandle);

   // Afficher le contenu brut du fichier JSON
   Print("Contenu brut du fichier JSON : ", jsonContent);

   // Si le fichier est vide, afficher un message
   if (StringLen(jsonContent) == 0 || jsonContent == "{}")
   {
      Print("Le fichier zones.json est vide. Veuillez générer les zones à partir des données de marché.");
      return;
   }

   // Parser les données JSON
   if (!ParseAndDrawZones(jsonContent))
   {
      Print("Erreur : Impossible de parser ou dessiner les zones.");
      return;
   }
}

bool WriteSymbolAndTimeframeToJson(string symbol, int timeframe)
{
   int fileHandle = FileOpen(ZonesFilePath, FILE_WRITE | FILE_TXT);
   if (fileHandle == INVALID_HANDLE)
   {
      Print("Erreur : Impossible d'ouvrir le fichier zones.json pour écriture.");
      return false;
   }

   // Créer un objet JSON avec la paire et le timeframe
   string jsonContent = "{\n";
   jsonContent += "  \"symbol\": \"" + symbol + "\",\n";
   jsonContent += "  \"timeframe\": " + IntegerToString(timeframe) + "\n";
   jsonContent += "}";

   // Écrire dans le fichier
   FileWrite(fileHandle, jsonContent);
   FileClose(fileHandle);

   Print("Fichier zones.json mis à jour avec la paire et le timeframe.");
   return true;
}

bool ParseAndDrawZones(string jsonContent)
{
   CJAVal zones;
   if (!zones.FromString(jsonContent))
   {
      Print("Erreur : Impossible de convertir le JSON en objet.");
      return false;
   }

   // Dessiner les supports
   for (int i = 0; i < zones["support"].Size(); i++)
   {
      double support = zones["support"].At(i).AsDouble();
      Print("Support détecté : ", DoubleToString(support, 5));
      DrawZone("Support_" + IntegerToString(i), support, support + 0.0005, clrGreen);
   }

   // Dessiner les résistances
   for (int i = 0; i < zones["resistance"].Size(); i++)
   {
      double resistance = zones["resistance"].At(i).AsDouble();
      Print("Résistance détectée : ", DoubleToString(resistance, 5));
      DrawZone("Resistance_" + IntegerToString(i), resistance, resistance - 0.0005, clrRed);
   }

   // Ajoutez les autres zones ici (Order Blocks, Equal Highs/Lows, etc.)
   // ...existing code...

   return true;
}

void DrawZone(string name, double price1, double price2, color zoneColor)
{
   long chart_id = ChartID();

   // Supprimer une zone existante avec le même nom
   ObjectDelete(chart_id, name);

   // Créer un rectangle pour représenter la zone
   if (!ObjectCreate(chart_id, name, OBJ_RECTANGLE, 0, TimeCurrent(), price1, TimeCurrent() + PeriodSeconds(PERIOD_D1), price2))
   {
      Print("Erreur lors de la création de la zone : ", name);
      return;
   }

   // Configurer les propriétés de la zone
   ObjectSetInteger(chart_id, name, OBJPROP_COLOR, zoneColor);
   ObjectSetInteger(chart_id, name, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(chart_id, name, OBJPROP_WIDTH, 2);
   ObjectSetInteger(chart_id, name, OBJPROP_BACK, true); // Envoyer à l'arrière-plan
}