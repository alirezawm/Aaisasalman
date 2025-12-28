package com.asiasalman.autoparts.ui.splash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.asiasalman.autoparts.R
import com.asiasalman.autoparts.ui.auth.LoginActivity
import com.asiasalman.autoparts.ui.main.MainActivity
import com.asiasalman.autoparts.util.TokenManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class SplashActivity : AppCompatActivity() {
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)
        
        // Check app config and maintenance mode
        checkAppConfig()
    }
    
    private fun checkAppConfig() {
        // TODO: Check app config from API
        // For now, just proceed to next screen
        
        Handler(Looper.getMainLooper()).postDelayed({
            navigateToNextScreen()
        }, 2000) // 2 seconds delay
    }
    
    private fun navigateToNextScreen() {
        val intent = if (tokenManager.isLoggedIn()) {
            Intent(this, MainActivity::class.java)
        } else {
            Intent(this, LoginActivity::class.java)
        }
        startActivity(intent)
        finish()
    }
}

