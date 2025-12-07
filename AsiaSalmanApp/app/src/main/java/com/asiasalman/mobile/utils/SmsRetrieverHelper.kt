package com.asiasalman.mobile.utils

import android.app.Activity
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import com.google.android.gms.auth.api.phone.SmsRetriever
import com.google.android.gms.common.api.CommonStatusCodes
import com.google.android.gms.common.api.Status
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

class SmsRetrieverHelper(private val activity: Activity) {
    
    fun startSmsRetriever(): Flow<String?> = callbackFlow {
        val client = SmsRetriever.getClient(activity)
        val task = client.startSmsRetriever()
        
        task.addOnSuccessListener {
            // SMS Retriever started successfully
        }
        
        task.addOnFailureListener {
            close(it)
        }
        
        val smsReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                if (SmsRetriever.SMS_RETRIEVED_ACTION == intent?.action) {
                    val extras = intent.extras
                    val status = extras?.get(SmsRetriever.EXTRA_STATUS) as? Status
                    
                    when (status?.statusCode) {
                        CommonStatusCodes.SUCCESS -> {
                            val message = extras.get(SmsRetriever.EXTRA_SMS_MESSAGE) as? String
                            message?.let {
                                // Extract OTP code (assuming 6 digits)
                                val otpRegex = Regex("""(\d{6})""")
                                val matchResult = otpRegex.find(it)
                                val otpCode = matchResult?.value
                                trySend(otpCode)
                            }
                        }
                        CommonStatusCodes.TIMEOUT -> {
                            close()
                        }
                    }
                }
            }
        }
        
        val intentFilter = IntentFilter(SmsRetriever.SMS_RETRIEVED_ACTION)
        activity.registerReceiver(smsReceiver, intentFilter)
        
        awaitClose {
            try {
                activity.unregisterReceiver(smsReceiver)
            } catch (e: Exception) {
                // Receiver might not be registered
            }
        }
    }
}

