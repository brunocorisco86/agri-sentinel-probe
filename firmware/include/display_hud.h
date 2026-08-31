#pragma once

#include "config.h"

#if defined(HAS_TFT_DISPLAY)
    #include <TFT_eSPI.h>
#endif

class DisplayHUD {
public:
    DisplayHUD();
    void begin();
    void showBootScreen(const String &version, const String &model);
    void showConfigAPScreen(const String &apSSID, const String &apIP);
    void showConnectingScreen(const String &targetSSID, uint8_t attempt);
    void updateHUD(const ProbeMetrics &metrics, const AppConfig &config);
    void showErrorScreen(const String &errorMessage);
    void updateStatusLED(DeviceState state, bool heartbeatTick);

private:
#if defined(HAS_TFT_DISPLAY)
    TFT_eSPI* _tft;
    TFT_eSprite* _spr;
    bool _initialized;
#endif

#if defined(HAS_STATUS_LED)
    uint8_t _ledPin;
    bool _ledInverted;
#endif
};

extern DisplayHUD hud;
