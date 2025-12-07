package com.asiasalman.mobile

import android.os.Bundle
import android.view.View
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection
import com.asiasalman.mobile.data.local.DataStoreManager
import com.asiasalman.mobile.ui.navigation.AsiaSalmanNavHost
import com.asiasalman.mobile.ui.theme.AsiaSalmanTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    @Inject
    lateinit var dataStoreManager: DataStoreManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Force RTL layout direction for the entire app
        window.decorView.layoutDirection = View.LAYOUT_DIRECTION_RTL
        
        setContent {
            // Read dark mode preference
            val darkModePreference by dataStoreManager.darkMode.collectAsState(initial = false)
            val isSystemDark = isSystemInDarkTheme()
            
            // Use user preference if set, otherwise use system
            val useDarkTheme = darkModePreference || (!darkModePreference && isSystemDark)
            
            // Apply RTL direction to all Compose content
            CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
                AsiaSalmanTheme(darkTheme = useDarkTheme) {
                    Surface(
                        modifier = Modifier.fillMaxSize(),
                        color = MaterialTheme.colorScheme.background
                    ) {
                        AsiaSalmanNavHost()
                    }
                }
            }
        }
    }
}
