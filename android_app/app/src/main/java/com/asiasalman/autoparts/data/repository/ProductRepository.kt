package com.asiasalman.autoparts.data.repository

import com.asiasalman.autoparts.data.model.*
import com.asiasalman.autoparts.data.remote.ApiService
import com.asiasalman.autoparts.util.TokenManager
import javax.inject.Inject

class ProductRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    suspend fun getProducts(
        page: Int = 1,
        perPage: Int = 20,
        brandId: Int? = null,
        categoryId: Int? = null,
        vehicleTypeId: Int? = null,
        minPrice: Int? = null,
        maxPrice: Int? = null,
        inStock: Boolean? = null,
        hasDiscount: Boolean? = null,
        search: String? = null
    ): Result<ProductsResponse> {
        return try {
            val token = tokenManager.getAccessToken()
            val response = apiService.getProducts(
                page, perPage, brandId, categoryId, vehicleTypeId,
                minPrice, maxPrice, inStock, hasDiscount, search,
                token?.let { "Bearer $it" }
            )
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در دریافت محصولات"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getProduct(productId: Int): Result<Product> {
        return try {
            val token = tokenManager.getAccessToken()
            val response = apiService.getProduct(productId, token?.let { "Bearer $it" })
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!.product)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در دریافت محصول"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun searchProducts(query: String, page: Int = 1, perPage: Int = 20): Result<ProductsResponse> {
        return try {
            val token = tokenManager.getAccessToken()
            val response = apiService.searchProducts(query, page, perPage, token?.let { "Bearer $it" })
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در جستجو"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getDailyDiscountProducts(limit: Int = 20, offset: Int = 0): Result<List<Product>> {
        return try {
            val token = tokenManager.getAccessToken()
            val response = apiService.getDailyDiscountProducts(limit, offset, token?.let { "Bearer $it" })
            if (response.isSuccessful && response.body()?.success == true) {
                Result.success(response.body()!!.data!!.products)
            } else {
                Result.failure(Exception(response.body()?.message ?: "خطا در دریافت محصولات تخفیف‌دار"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

