package com.asiasalman.mobile.data.remote

import com.asiasalman.mobile.data.model.*
import retrofit2.http.*

interface ApiService {
    
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
        @Query("category_id") categoryId: Int? = null,
        @Query("discounted") discounted: Boolean? = null
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
    
    @GET("products/discounted")
    suspend fun getDiscountedProducts(
        @Header("Authorization") token: String? = null,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 10
    ): ApiResponse<ProductsResponse>
    
    // Categories
    @GET("categories")
    suspend fun getCategories(): ApiResponse<List<Category>>
    
    @GET("categories/vehicle-based")
    suspend fun getVehicleBasedCategories(): ApiResponse<List<Category>>
    
    @GET("categories/brand-based")
    suspend fun getBrandBasedCategories(): ApiResponse<List<Category>>
    
    @GET("categories/{id}/products")
    suspend fun getCategoryProducts(
        @Path("id") categoryId: Int,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20
    ): ApiResponse<ProductsResponse>
    
    // Brands
    @GET("brands")
    suspend fun getBrands(): ApiResponse<List<Brand>>
    
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
    
    @DELETE("cart")
    suspend fun clearCart(@Header("Authorization") token: String): ApiResponse<Unit>
    
    // Orders
    @GET("orders")
    suspend fun getOrders(
        @Header("Authorization") token: String,
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 10
    ): ApiResponse<List<Order>>
    
    @POST("orders")
    suspend fun createOrder(
        @Header("Authorization") token: String,
        @Body request: CreateOrderRequest
    ): ApiResponse<Order>
    
    @GET("orders/{id}")
    suspend fun getOrder(
        @Header("Authorization") token: String,
        @Path("id") orderId: Int
    ): ApiResponse<Order>
    
    @GET("orders/pending")
    suspend fun getPendingOrders(
        @Header("Authorization") token: String
    ): ApiResponse<List<Order>>
    
    // User Profile
    @GET("user/profile")
    suspend fun getUserProfile(@Header("Authorization") token: String): ApiResponse<User>
    
    @PUT("user/profile")
    suspend fun updateProfile(
        @Header("Authorization") token: String,
        @Body request: Map<String, Any>
    ): ApiResponse<User>
    
    @POST("user/bulk-buyer-request")
    suspend fun requestBulkBuyer(
        @Header("Authorization") token: String,
        @Body request: Map<String, Any>
    ): ApiResponse<Map<String, Any>>
    
    // Config & Banners
    @GET("config")
    suspend fun getConfig(): ApiResponse<Map<String, Any>>
    
    @GET("banners")
    suspend fun getBanners(): ApiResponse<BannersResponse>
    
    @GET("config/company-info")
    suspend fun getCompanyInfo(): ApiResponse<CompanyInfo>
    
    // Home Sections
    @GET("home-sections")
    suspend fun getHomeSections(): ApiResponse<HomeSectionsResponse>
    
    // Settings
    @GET("settings/contact")
    suspend fun getContactInfo(): ApiResponse<ContactInfo>
    
    @GET("settings/about")
    suspend fun getAboutInfo(): ApiResponse<AboutInfo>
    
    // Featured Products
    @GET("products")
    suspend fun getFeaturedProducts(
        @Header("Authorization") token: String? = null,
        @Query("featured") featured: String? = null, // bestselling, discounted, new, special
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 10
    ): ApiResponse<ProductsResponse>
    
    // Rewards
    @GET("rewards")
    suspend fun getRewards(
        @Header("Authorization") token: String? = null
    ): ApiResponse<List<Reward>>
    
    // Suggestions
    @GET("suggestions/daily")
    suspend fun getDailySuggestions(
        @Header("Authorization") token: String? = null
    ): ApiResponse<List<Product>>
    
    @GET("suggestions/personalized")
    suspend fun getPersonalizedSuggestions(
        @Header("Authorization") token: String
    ): ApiResponse<List<Product>>
}

