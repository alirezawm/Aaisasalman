/**
 * نمونه کدهای Android برای اتصال به API
 * Android Code Samples for API Integration
 * 
 * این فایل شامل نمونه کدهای Kotlin برای اتصال به API موبایل است
 */

package com.asiasalman.mobile

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName

// ==================== Configuration ====================

object ApiConfig {
    const val BASE_URL = "https://www.asiasalman.com/api/mobile/v1/"
    const val TIMEOUT_SECONDS = 30L
}

// ==================== Data Models ====================

data class ApiResponse<T>(
    @SerializedName("success") val success: Boolean,
    @SerializedName("message") val message: String?,
    @SerializedName("data") val data: T?,
    @SerializedName("code") val code: String?
)

data class SendOtpRequest(
    @SerializedName("phone") val phone: String
)

data class VerifyOtpRequest(
    @SerializedName("phone") val phone: String,
    @SerializedName("otp_code") val otpCode: String
)

data class AuthResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("user") val user: User
)

data class User(
    @SerializedName("id") val id: Int,
    @SerializedName("full_name") val fullName: String,
    @SerializedName("phone") val phone: String,
    @SerializedName("email") val email: String?
)

data class Product(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_en") val nameEn: String?,
    @SerializedName("sku") val sku: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("primary_image") val primaryImage: String?,
    @SerializedName("images") val images: List<String>?,
    @SerializedName("retail_price_cash") val retailPriceCash: Double,
    @SerializedName("retail_price_check") val retailPriceCheck: Double,
    @SerializedName("bulk_price_cash") val bulkPriceCash: Double?,
    @SerializedName("bulk_price_check") val bulkPriceCheck: Double?,
    @SerializedName("stock_quantity") val stockQuantity: Int?,
    @SerializedName("brand") val brand: Brand?,
    @SerializedName("category") val category: Category?
)

data class Brand(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_fa") val nameFa: String,
    @SerializedName("logo") val logo: String?
)

data class Category(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_en") val nameEn: String?
)

data class ProductsResponse(
    @SerializedName("products") val products: List<Product>,
    @SerializedName("pagination") val pagination: Pagination
)

data class Pagination(
    @SerializedName("page") val page: Int,
    @SerializedName("per_page") val perPage: Int,
    @SerializedName("total") val total: Int,
    @SerializedName("pages") val pages: Int,
    @SerializedName("has_next") val hasNext: Boolean,
    @SerializedName("has_prev") val hasPrev: Boolean
)

data class CartItem(
    @SerializedName("id") val id: Int,
    @SerializedName("product") val product: Product,
    @SerializedName("quantity") val quantity: Int,
    @SerializedName("price_type") val priceType: String,
    @SerializedName("unit_price") val unitPrice: Double,
    @SerializedName("total_price") val totalPrice: Double
)

data class CartResponse(
    @SerializedName("cash_cart") val cashCart: Cart,
    @SerializedName("check_cart") val checkCart: Cart,
    @SerializedName("grand_total") val grandTotal: Double,
    @SerializedName("total_items") val totalItems: Int
)

data class Cart(
    @SerializedName("items") val items: List<CartItem>,
    @SerializedName("total") val total: Double,
    @SerializedName("item_count") val itemCount: Int
)

data class AddToCartRequest(
    @SerializedName("product_id") val productId: Int,
    @SerializedName("quantity") val quantity: Int,
    @SerializedName("price_type") val priceType: String,
    @SerializedName("price_plan") val pricePlan: String? = null
)

data class UpdateCartRequest(
    @SerializedName("quantity") val quantity: Int
)

data class CreateOrderRequest(
    @SerializedName("payment_type") val paymentType: String,
    @SerializedName("customer_notes") val customerNotes: String? = null
)

// ==================== API Interface ====================

interface MobileApiService {
    
    // Authentication
    @POST("auth/send-otp")
    suspend fun sendOtp(@Body request: SendOtpRequest): ApiResponse<Map<String, Any>>
    
    @POST("auth/verify-otp")
    suspend fun verifyOtp(@Body request: VerifyOtpRequest): ApiResponse<AuthResponse>
    
    @POST("auth/refresh-token")
    suspend fun refreshToken(@Header("Authorization") token: String): ApiResponse<Map<String, String>>
    
    @POST("auth/logout")
    suspend fun logout(@Header("Authorization") token: String): ApiResponse<Unit>
    
    // Products
    @GET("products")
    suspend fun getProducts(
        @Header("Authorization") token: String? = null,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("brand_id") brandId: Int? = null,
        @Query("category_id") categoryId: Int? = null
    ): ApiResponse<ProductsResponse>
    
    @GET("products/{id}")
    suspend fun getProduct(
        @Header("Authorization") token: String? = null,
        @Path("id") productId: Int
    ): ApiResponse<Product>
    
    @GET("products/search")
    suspend fun searchProducts(
        @Header("Authorization") token: String? = null,
        @Query("q") query: String,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20
    ): ApiResponse<ProductsResponse>
    
    @GET("products/filters")
    suspend fun getFilters(): ApiResponse<Map<String, Any>>
    
    // Categories
    @GET("categories")
    suspend fun getCategories(): ApiResponse<List<Category>>
    
    @GET("categories/vehicle-based")
    suspend fun getVehicleBasedCategories(
        @Header("Authorization") token: String? = null
    ): ApiResponse<List<Any>>
    
    @GET("categories/brand-based")
    suspend fun getBrandBasedCategories(): ApiResponse<List<Any>>
    
    // Cart
    @GET("cart")
    suspend fun getCart(@Header("Authorization") token: String): ApiResponse<CartResponse>
    
    @POST("cart")
    suspend fun addToCart(
        @Header("Authorization") token: String,
        @Body request: AddToCartRequest
    ): ApiResponse<Map<String, Any>>
    
    @PUT("cart/{id}")
    suspend fun updateCartItem(
        @Header("Authorization") token: String,
        @Path("id") cartItemId: Int,
        @Body request: UpdateCartRequest
    ): ApiResponse<Map<String, Any>>
    
    @DELETE("cart/{id}")
    suspend fun removeFromCart(
        @Header("Authorization") token: String,
        @Path("id") cartItemId: Int
    ): ApiResponse<Unit>
    
    // Orders
    @GET("orders")
    suspend fun getOrders(
        @Header("Authorization") token: String,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 10
    ): ApiResponse<Map<String, Any>>
    
    @POST("orders")
    suspend fun createOrder(
        @Header("Authorization") token: String,
        @Body request: CreateOrderRequest
    ): ApiResponse<Map<String, Any>>
    
    @GET("orders/{id}")
    suspend fun getOrder(
        @Header("Authorization") token: String,
        @Path("id") orderId: Int
    ): ApiResponse<Map<String, Any>>
    
    // User Profile
    @GET("user/profile")
    suspend fun getUserProfile(@Header("Authorization") token: String): ApiResponse<Map<String, Any>>
    
    @PUT("user/profile")
    suspend fun updateProfile(
        @Header("Authorization") token: String,
        @Body request: Map<String, Any>
    ): ApiResponse<Map<String, Any>>
    
    // Config
    @GET("config")
    suspend fun getConfig(): ApiResponse<Map<String, Any>>
    
    @GET("config/banners")
    suspend fun getBanners(): ApiResponse<Map<String, Any>>
    
    @GET("config/company-info")
    suspend fun getCompanyInfo(): ApiResponse<Map<String, Any>>
    
    @GET("config/splash")
    suspend fun getSplashConfig(): ApiResponse<Map<String, Any>>
    
    @GET("rewards")
    suspend fun getRewards(@Header("Authorization") token: String? = null): ApiResponse<Map<String, Any>>
}

// ==================== Retrofit Setup ====================

object ApiClient {
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(ApiConfig.TIMEOUT_SECONDS, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(ApiConfig.TIMEOUT_SECONDS, java.util.concurrent.TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(Gson()))
        .build()
    
    val apiService: MobileApiService = retrofit.create(MobileApiService::class.java)
}

// ==================== Token Manager ====================

object TokenManager {
    private const val PREF_NAME = "api_prefs"
    private const val KEY_ACCESS_TOKEN = "access_token"
    private const val KEY_REFRESH_TOKEN = "refresh_token"
    
    // در پروژه واقعی از SharedPreferences استفاده کنید
    private var accessToken: String? = null
    private var refreshToken: String? = null
    
    fun saveTokens(access: String, refresh: String) {
        accessToken = access
        refreshToken = refresh
        // SharedPreferences را ذخیره کنید
    }
    
    fun getAccessToken(): String? = accessToken
    fun getRefreshToken(): String? = refreshToken
    
    fun clearTokens() {
        accessToken = null
        refreshToken = null
        // SharedPreferences را پاک کنید
    }
    
    fun getAuthHeader(): String? {
        return accessToken?.let { "Bearer $it" }
    }
}

// ==================== Usage Examples ====================

/*
// مثال استفاده در ViewModel یا Repository:

class ProductRepository {
    private val apiService = ApiClient.apiService
    
    suspend fun getProducts(page: Int = 1): Result<ProductsResponse> {
        return try {
            val token = TokenManager.getAuthHeader()
            val response = apiService.getProducts(token, page)
            
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(Exception(response.message ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    suspend fun sendOtp(phone: String): Result<Unit> {
        return try {
            val request = SendOtpRequest(phone)
            val response = apiService.sendOtp(request)
            
            if (response.success) {
                Result.Success(Unit)
            } else {
                Result.Error(Exception(response.message ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    suspend fun verifyOtp(phone: String, otpCode: String): Result<AuthResponse> {
        return try {
            val request = VerifyOtpRequest(phone, otpCode)
            val response = apiService.verifyOtp(request)
            
            if (response.success && response.data != null) {
                // ذخیره توکن‌ها
                TokenManager.saveTokens(
                    response.data.accessToken,
                    response.data.refreshToken
                )
                Result.Success(response.data)
            } else {
                Result.Error(Exception(response.message ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}
*/

