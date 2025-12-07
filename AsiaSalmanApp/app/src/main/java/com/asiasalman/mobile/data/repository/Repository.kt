package com.asiasalman.mobile.data.repository

import com.asiasalman.mobile.data.local.TokenManager
import com.asiasalman.mobile.data.model.*
import com.asiasalman.mobile.data.remote.ApiService
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

@Singleton
class Repository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) {
    private suspend fun getAuthHeader(): String? {
        return tokenManager.getAccessToken()?.let { "Bearer $it" }
    }
    
    // Auth
    suspend fun sendOtp(phone: String): Result<Unit> {
        return try {
            val response = apiService.sendOtp(SendOtpRequest(phone))
            if (response.success) {
                tokenManager.saveUserPhone(phone)
                Result.Success(Unit)
            } else {
                Result.Error(response.message ?: "خطا در ارسال کد")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun verifyOtp(phone: String, otpCode: String): Result<AuthResponse> {
        return try {
            val response = apiService.verifyOtp(VerifyOtpRequest(phone, otpCode))
            if (response.success && response.data != null) {
                tokenManager.saveTokens(response.data.accessToken, response.data.refreshToken)
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "کد تایید نادرست است")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun logout(): Result<Unit> {
        return try {
            val token = getAuthHeader()
            if (token != null) {
                apiService.logout(token)
            }
            tokenManager.clearTokens()
            Result.Success(Unit)
        } catch (e: Exception) {
            tokenManager.clearTokens()
            Result.Success(Unit)
        }
    }
    
    // Products
    suspend fun getProducts(
        page: Int = 1,
        perPage: Int = 20,
        brandId: Int? = null,
        categoryId: Int? = null,
        discounted: Boolean? = null
    ): Result<ProductsResponse> {
        return try {
            val response = apiService.getProducts(
                token = getAuthHeader(),
                page = page,
                perPage = perPage,
                brandId = brandId,
                categoryId = categoryId,
                discounted = discounted
            )
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت محصولات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun getProduct(productId: Int): Result<Product> {
        return try {
            val response = apiService.getProduct(getAuthHeader(), productId)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت محصول")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun searchProducts(query: String, page: Int = 1): Result<ProductsResponse> {
        return try {
            val response = apiService.searchProducts(getAuthHeader(), query, page)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در جستجو")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun getDiscountedProducts(page: Int = 1): Result<ProductsResponse> {
        return try {
            val response = apiService.getDiscountedProducts(getAuthHeader(), page)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت محصولات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Categories
    suspend fun getCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getCategories()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت دسته‌بندی‌ها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun getVehicleCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getVehicleBasedCategories()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت دسته‌بندی‌ها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun getBrandCategories(): Result<List<Category>> {
        return try {
            val response = apiService.getBrandBasedCategories()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت دسته‌بندی‌ها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Cart
    suspend fun getCart(): Result<CartResponse> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val response = apiService.getCart(token)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت سبد خرید")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun addToCart(productId: Int, quantity: Int, priceType: String): Result<Unit> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val request = AddToCartRequest(productId, quantity, priceType)
            val response = apiService.addToCart(token, request)
            if (response.success) {
                Result.Success(Unit)
            } else {
                Result.Error(response.message ?: "خطا در افزودن به سبد")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun updateCartItem(cartItemId: Int, quantity: Int): Result<Unit> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val response = apiService.updateCartItem(token, cartItemId, UpdateCartRequest(quantity))
            if (response.success) {
                Result.Success(Unit)
            } else {
                Result.Error(response.message ?: "خطا در به‌روزرسانی")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun removeFromCart(cartItemId: Int): Result<Unit> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val response = apiService.removeFromCart(token, cartItemId)
            if (response.success) {
                Result.Success(Unit)
            } else {
                Result.Error(response.message ?: "خطا در حذف")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Orders
    suspend fun getOrders(page: Int = 1): Result<List<Order>> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val response = apiService.getOrders(token, page)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت سفارشات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun createOrder(paymentType: String, notes: String? = null): Result<Order> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val request = CreateOrderRequest(paymentType, notes)
            val response = apiService.createOrder(token, request)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در ثبت سفارش")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Profile
    suspend fun getUserProfile(): Result<User> {
        return try {
            val token = getAuthHeader() ?: return Result.Error("لطفا وارد شوید")
            val response = apiService.getUserProfile(token)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت پروفایل")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Banners
    suspend fun getBanners(): Result<List<Banner>> {
        return try {
            val response = apiService.getBanners()
            if (response.success && response.data != null) {
                Result.Success(response.data.banners)
            } else {
                Result.Error(response.message ?: "خطا در دریافت بنرها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Rewards
    suspend fun getRewards(): Result<List<Reward>> {
        return try {
            val response = apiService.getRewards(getAuthHeader())
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت جوایز")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Suggestions
    suspend fun getDailySuggestions(): Result<List<Product>> {
        return try {
            val response = apiService.getDailySuggestions(getAuthHeader())
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت پیشنهادات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Company Info
    suspend fun getCompanyInfo(): Result<CompanyInfo> {
        return try {
            val response = apiService.getCompanyInfo()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت اطلاعات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Brands
    suspend fun getBrands(): Result<List<Brand>> {
        return try {
            val response = apiService.getBrands()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت برندها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Home Sections
    suspend fun getHomeSections(): Result<List<HomeSection>> {
        return try {
            val response = apiService.getHomeSections()
            if (response.success && response.data != null) {
                Result.Success(response.data.sections.filter { it.enabled }.sortedBy { it.order })
            } else {
                Result.Error(response.message ?: "خطا در دریافت دسته‌بندی‌ها")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Featured Products
    suspend fun getFeaturedProducts(
        featured: String,
        page: Int = 1,
        perPage: Int = 10
    ): Result<ProductsResponse> {
        return try {
            val response = apiService.getFeaturedProducts(getAuthHeader(), featured, page, perPage)
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت محصولات")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    // Settings
    suspend fun getContactInfo(): Result<ContactInfo> {
        return try {
            val response = apiService.getContactInfo()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت اطلاعات تماس")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    suspend fun getAboutInfo(): Result<AboutInfo> {
        return try {
            val response = apiService.getAboutInfo()
            if (response.success && response.data != null) {
                Result.Success(response.data)
            } else {
                Result.Error(response.message ?: "خطا در دریافت اطلاعات درباره ما")
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "خطا در اتصال به سرور")
        }
    }
    
    fun isLoggedIn() = tokenManager.isLoggedIn
}

