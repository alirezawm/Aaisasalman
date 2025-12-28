package com.asiasalman.autoparts

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class AsiaSalmanApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
    }
}

