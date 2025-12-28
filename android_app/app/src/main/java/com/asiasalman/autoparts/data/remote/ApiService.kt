package com.asiasalman.autoparts.data.remote

import com.asiasalman.autoparts.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Authentication
    @POST("auth/send-otp")
    suspend fun sendOTP(@Body request: SendOTPRequest): Response<ApiResponse<OTPResponse>>
    
    @POST("auth/verify-otp")
    suspend fun verifyOTP(@Body request: VerifyOTPRequest): Response<ApiResponse<AuthResponse>>
    
    @POST("auth/refresh-token")
    suspend fun refreshToken(@Header("Authorization") token: String): Response<ApiResponse<RefreshTokenResponse>>
    
    @POST("auth/logout")
    suspend fun logout(@Header("Authorization") token: String): Response<ApiResponse<Unit>>
    
    // Products
    @GET("products")
    suspend fun getProducts(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("brand_id") brandId: Int? = null,
        @Query("category_id") categoryId: Int? = null,
        @Query("vehicle_type_id") vehicleTypeId: Int? = null,
        @Query("min_price") minPrice: Int? = null,
        @Query("max_price") maxPrice: Int? = null,
        @Query("in_stock") inStock: Boolean? = null,
        @Query("has_discount") hasDiscount: Boolean? = null,
        @Query("search") search: String? = null,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<ProductsResponse>>
    
    @GET("products/{id}")
    suspend fun getProduct(
        @Path("id") productId: Int,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<ProductDetailResponse>>
    
    @GET("products/search")
    suspend fun searchProducts(
        @Query("q") query: String,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<ProductsResponse>>
    
    @GET("products/filters")
    suspend fun getFilters(): Response<ApiResponse<FiltersResponse>>
    
    // Categories
    @GET("categories")
    suspend fun getCategories(): Response<ApiResponse<CategoriesResponse>>
    
    @GET("categories/vehicle-based")
    suspend fun getCategoriesByVehicle(
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<VehicleCategoriesResponse>>
    
    @GET("categories/brand-based")
    suspend fun getCategoriesByBrand(
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<BrandCategoriesResponse>>
    
    @GET("categories/{id}/products")
    suspend fun getCategoryProducts(
        @Path("id") categoryId: Int,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<ProductsResponse>>
    
    // Discounts
    @GET("discounts/daily-products")
    suspend fun getDailyDiscountProducts(
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<DiscountProductsResponse>>
    
    @GET("discounts/monthly-products")
    suspend fun getMonthlyDiscountProducts(
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0,
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<DiscountProductsResponse>>
    
    // Cart
    @GET("cart")
    suspend fun getCart(
        @Query("price_type") priceType: String? = null,
        @Header("Authorization") token: String
    ): Response<ApiResponse<Cart>>
    
    @POST("cart")
    suspend fun addToCart(
        @Body request: AddToCartRequest,
        @Header("Authorization") token: String
    ): Response<ApiResponse<AddToCartResponse>>
    
    @PUT("cart/{id}")
    suspend fun updateCartItem(
        @Path("id") cartItemId: Int,
        @Body request: UpdateCartRequest,
        @Header("Authorization") token: String
    ): Response<ApiResponse<Unit>>
    
    @DELETE("cart/{id}")
    suspend fun removeFromCart(
        @Path("id") cartItemId: Int,
        @Header("Authorization") token: String
    ): Response<ApiResponse<Unit>>
    
    @DELETE("cart/clear")
    suspend fun clearCart(
        @Query("price_type") priceType: String? = null,
        @Header("Authorization") token: String
    ): Response<ApiResponse<Unit>>
    
    // User
    @GET("user/profile")
    suspend fun getUserProfile(
        @Header("Authorization") token: String
    ): Response<ApiResponse<UserProfileResponse>>
    
    @PUT("user/profile")
    suspend fun updateUserProfile(
        @Body request: UpdateProfileRequest,
        @Header("Authorization") token: String
    ): Response<ApiResponse<UpdateProfileResponse>>
    
    @POST("user/bulk-buyer-request")
    suspend fun submitBulkBuyerRequest(
        @Body request: BulkBuyerRequest,
        @Header("Authorization") token: String
    ): Response<ApiResponse<BulkBuyerResponse>>
    
    @GET("user/notifications")
    suspend fun getNotifications(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("unread_only") unreadOnly: Boolean = false,
        @Header("Authorization") token: String
    ): Response<ApiResponse<NotificationsResponse>>
    
    @POST("user/notifications/{id}/read")
    suspend fun markNotificationRead(
        @Path("id") notificationId: Int,
        @Header("Authorization") token: String
    ): Response<ApiResponse<Unit>>
    
    // Company
    @GET("company/info")
    suspend fun getCompanyInfo(): Response<ApiResponse<CompanyInfo>>
    
    @GET("company/banners")
    suspend fun getBanners(
        @Query("position") position: String = "homepage"
    ): Response<ApiResponse<BannersResponse>>
    
    // App Config
    @GET("app/config")
    suspend fun getAppConfig(
        @Header("Authorization") token: String? = null
    ): Response<ApiResponse<AppConfig>>
}

// Request Models
data class SendOTPRequest(val phone: String)
data class VerifyOTPRequest(val phone: String, val otpCode: String)
data class AddToCartRequest(
    val productId: Int,
    val quantity: Int,
    val priceType: String,
    val pricePlan: String? = null
)
data class UpdateCartRequest(val quantity: Int)
data class UpdateProfileRequest(
    val fullName: String? = null,
    val email: String? = null,
    val companyName: String? = null,
    val nationalId: String? = null,
    val birthDate: String? = null,
    val address: String? = null,
    val landlinePhone: String? = null,
    val secondaryPhone: String? = null
)
data class BulkBuyerRequest(
    val companyName: String,
    val nationalId: String,
    val address: String,
    val landlinePhone: String,
    val description: String? = null
)

// Response Models
data class OTPResponse(val expiresIn: Int)
data class RefreshTokenResponse(val accessToken: String)
data class ProductDetailResponse(val product: Product, val relatedProducts: List<Product>)
data class FiltersResponse(
    val brands: List<Brand>,
    val categories: List<Category>,
    val vehicleTypes: List<VehicleType>,
    val productTypes: List<ProductType>,
    val priceRange: PriceRange
)
data class PriceRange(val min: Int, val max: Int)
data class CategoriesResponse(val categories: List<Category>)
data class VehicleCategoriesResponse(val vehicleTypes: List<VehicleTypeWithCategories>)
data class BrandCategoriesResponse(val brands: List<BrandWithCategories>)
data class VehicleTypeWithCategories(
    val id: Int,
    val name: String,
    val nameFa: String,
    val iconUrl: String,
    val categories: List<Category>
)
data class BrandWithCategories(
    val id: Int,
    val name: String,
    val nameFa: String,
    val logoUrl: String,
    val categories: List<Category>
)
data class DiscountProductsResponse(
    val products: List<Product>,
    val discountInfo: DiscountInfo?
)
data class DiscountInfo(
    val name: String,
    val nameFa: String,
    val discountPercentage: Float
)
data class AddToCartResponse(val cartItem: CartItemData)
data class CartItemData(
    val id: Int,
    val productId: Int,
    val quantity: Int,
    val priceType: String
)
data class UserProfileResponse(val user: User)
data class UpdateProfileResponse(val user: UserData)
data class UserData(
    val id: Int,
    val fullName: String,
    val profileCompletionPercentage: Int
)
data class BulkBuyerResponse(val requestStatus: String)
data class NotificationsResponse(
    val notifications: List<Notification>,
    val unreadCount: Int,
    val pagination: Pagination
)
data class Notification(
    val id: Int,
    val title: String,
    val message: String,
    val type: String,
    val isRead: Boolean,
    val createdAt: String?,
    val actionUrl: String?
)
data class CompanyInfo(
    val name: String,
    val nameFa: String,
    val logoUrl: String,
    val description: String,
    val descriptionFa: String,
    val phone: String,
    val supportPhone: String,
    val email: String,
    val address: String,
    val about: String,
    val aboutFa: String,
    val partnerBrands: List<Brand>
)
data class BannersResponse(val banners: List<Banner>)
data class Banner(
    val id: Int,
    val title: String,
    val titleFa: String,
    val imageUrl: String,
    val linkUrl: String?,
    val position: String,
    val isActive: Boolean
)
data class AppConfig(
    val appVersion: String,
    val minAppVersion: String,
    val forceUpdate: Boolean,
    val maintenanceMode: Boolean,
    val maintenanceMessage: String,
    val features: Features,
    val settings: Settings,
    val dailySuggestions: DailySuggestions,
    val company: CompanyConfig
)
data class Features(
    val dailySuggestionsEnabled: Boolean,
    val wholesaleRequestsEnabled: Boolean,
    val walletEnabled: Boolean,
    val notificationsEnabled: Boolean
)
data class Settings(
    val defaultPriceType: String,
    val showBulkPrices: Boolean,
    val enableOfflineMode: Boolean
)
data class DailySuggestions(
    val enabled: Boolean,
    val title: String,
    val titleFa: String,
    val products: List<Product>,
    val updatedAt: String?
)
data class CompanyConfig(
    val name: String,
    val nameFa: String,
    val logoUrl: String,
    val phone: String,
    val supportPhone: String,
    val email: String,
    val address: String,
    val partnerBrands: List<Brand>
)

