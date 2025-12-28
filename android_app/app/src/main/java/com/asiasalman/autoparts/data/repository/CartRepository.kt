package com.asiasalman.autoparts.data.repository

import com.asiasalman.autoparts.data.model.*
import com.asiasalman.autoparts.data.remote.AddToCartRequest
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.data.remote.CartItemData
import com.asiasalman.autoparts.data.remote.UpdateCartRequest
import com.asiasalman.autoparts.util.TokenManager
import javax.inject.Inject

class CartRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    private fun getAuthToken(): String {
        return "Bearer ${tokenManager.getAccessToken() ?: throw Exception("Not authenticated")}"
    }
    
    suspend fun getCart(priceType: String? = null): Result<Cart> {
        return try {
            val response = apiService.getCart(priceType, getAuthToken())
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در دریافت سبد خرید"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun addToCart(
        productId: Int,
        quantity: Int,
        priceType: String,
        pricePlan: String? = null
    ): Result<CartItemData> {
        return try {
            val response = apiService.addToCart(
                AddToCartRequest(productId, quantity, priceType, pricePlan),
                getAuthToken()
            )
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!.cartItem)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در افزودن به سبد خرید"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun updateCartItem(cartItemId: Int, quantity: Int): Result<Unit> {
        return try {
            val response = apiService.updateCartItem(
                cartItemId,
                UpdateCartRequest(quantity),
                getAuthToken()
            )
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در به‌روزرسانی سبد خرید"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun removeFromCart(cartItemId: Int): Result<Unit> {
        return try {
            val response = apiService.removeFromCart(cartItemId, getAuthToken())
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در حذف از سبد خرید"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun clearCart(priceType: String? = null): Result<Unit> {
        return try {
            val response = apiService.clearCart(priceType, getAuthToken())
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در پاک کردن سبد خرید"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

