package com.asiasalman.mobile.utils

import android.Manifest
import android.os.Build
import androidx.annotation.RequiresApi

object PermissionHelper {
    const val READ_SMS = Manifest.permission.READ_SMS
    const val RECEIVE_SMS = Manifest.permission.RECEIVE_SMS
    
    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    const val POST_NOTIFICATIONS = Manifest.permission.POST_NOTIFICATIONS

    fun getRequiredPermissions(): List<String> {
        val permissions = mutableListOf<String>(
            READ_SMS,
            RECEIVE_SMS
        )
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(POST_NOTIFICATIONS)
        }
        
        return permissions
    }
}

