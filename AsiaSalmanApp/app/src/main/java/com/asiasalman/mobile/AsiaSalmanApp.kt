package com.asiasalman.mobile

import android.app.Application
import android.content.res.Configuration
import android.view.View
import dagger.hilt.android.HiltAndroidApp
import java.util.Locale

@HiltAndroidApp
class AsiaSalmanApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // Force Persian locale and RTL for the entire application
        forceRtlLayout()
    }
    
    private fun forceRtlLayout() {
        // Set Persian locale
        val persianLocale = Locale("fa", "IR")
        Locale.setDefault(persianLocale)
        
        val config = Configuration(resources.configuration)
        config.setLocale(persianLocale)
        config.setLayoutDirection(persianLocale)
        
        resources.updateConfiguration(config, resources.displayMetrics)
    }
    
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Re-apply RTL on configuration change
        forceRtlLayout()
    }
}
