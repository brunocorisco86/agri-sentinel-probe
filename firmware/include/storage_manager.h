#pragma once

#include "config.h"
#include <Preferences.h>

class StorageManager {
public:
    StorageManager();
    bool begin();
    bool loadConfig(AppConfig &config);
    bool saveConfig(const AppConfig &config);
    void resetConfig();

private:
    Preferences _prefs;
};

extern StorageManager storage;
