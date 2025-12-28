package com.asiasalman.autoparts.data.repository

import com.asiasalman.autoparts.data.model.*
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.data.remote.OTPResponse
import com.asiasalman.autoparts.data.remote.SendOTPRequest
import com.asiasalman.autoparts.data.remote.VerifyOTPRequest
import com.asiasalman.autoparts.util.TokenManager
import com.google.gson.Gson
import com.google.gson.JsonObject
import okhttp3.ResponseBody
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager,
    private val gson: Gson
) {
    private fun parseErrorResponse(errorBody: ResponseBody?): String? {
        return try {
            errorBody?.let {
                // Use string() instead of charStream() to avoid stream consumption issues
                val jsonString = it.string()
                val jsonObject = gson.fromJson(jsonString, JsonObject::class.java)
                jsonObject.get("message")?.asString
            }
        } catch (e: Exception) {
            null
        }
    }
    
    suspend fun sendOTP(phone: String): Result<OTPResponse> {
        return try {
            // Normalize phone number (remove any non-digit characters)
            val cleanPhone = phone.replace(Regex("[^0-9]"), "")
            val response = apiService.sendOTP(SendOTPRequest(cleanPhone))
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!)
            } else {
                val errorMessage = response.body()?.message 
                    ?: parseErrorResponse(response.errorBody())
                    ?: "خطا در ارسال کد تایید"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: HttpException) {
            val errorMessage = parseErrorResponse(e.response()?.errorBody()) 
                ?: "خطا در ارسال کد تایید"
            Result.failure(Exception(errorMessage))
        } catch (e: IOException) {
            Result.failure(Exception("خطا در اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun verifyOTP(phone: String, otpCode: String): Result<AuthResponse> {
        return try {
            // Normalize phone number and OTP code (remove any non-digit characters)
            val cleanPhone = phone.replace(Regex("[^0-9]"), "")
            val cleanOtpCode = otpCode.replace(Regex("[^0-9]"), "").trim()
            
            val response = apiService.verifyOTP(VerifyOTPRequest(cleanPhone, cleanOtpCode))
            if (response.isSuccessful && response.body()?.success == true) {
                val authResponse = response.body()!!.data!!
                tokenManager.saveAccessToken(authResponse.accessToken)
                tokenManager.saveRefreshToken(authResponse.refreshToken)
                Result.success(authResponse)
            } else {
                val errorMessage = response.body()?.message 
                    ?: parseErrorResponse(response.errorBody())
                    ?: "کد تایید معتبر نیست"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: HttpException) {
            val errorMessage = parseErrorResponse(e.response()?.errorBody()) 
                ?: "کد تایید معتبر نیست"
            Result.failure(Exception(errorMessage))
        } catch (e: IOException) {
            Result.failure(Exception("خطا در اتصال به سرور. لطفاً اتصال اینترنت خود را بررسی کنید."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(): Result<String> {
        return try {
            val refreshToken = tokenManager.getRefreshToken()
                ?: return Result.failure(Exception("Refresh token not found"))
            
            val response = apiService.refreshToken("Bearer $refreshToken")
            if (response.isSuccessful && response.body()?.success == true) {
                val newToken = response.body()!!.data!!.accessToken
                tokenManager.saveAccessToken(newToken)
                Result.success(newToken)
            } else {
                Result.failure(Exception("Failed to refresh token"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout(): Result<Unit> {
        return try {
            val token = tokenManager.getAccessToken()
            if (token != null) {
                apiService.logout("Bearer $token")
            }
            tokenManager.clearTokens()
            Result.success(Unit)
        } catch (e: Exception) {
            tokenManager.clearTokens()
            Result.success(Unit) // Always clear tokens even if API call fails
        }
    }
}

