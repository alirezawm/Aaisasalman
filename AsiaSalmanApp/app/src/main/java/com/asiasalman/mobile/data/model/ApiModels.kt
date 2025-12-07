package com.asiasalman.mobile.data.model

import com.google.gson.annotations.SerializedName

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
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String,
    @SerializedName("email") val email: String?,
    @SerializedName("is_bulk_buyer") val isBulkBuyer: Boolean = false
)

data class Product(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_en") val nameEn: String?,
    @SerializedName("sku") val sku: String?,
    @SerializedName("oem_code") val oemCode: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("description_full") val descriptionFull: String?,
    @SerializedName("primary_image") val primaryImage: String?,
    @SerializedName("images") val images: List<String>?,
    @SerializedName("retail_price_cash") val retailPriceCash: Double,
    @SerializedName("retail_price_check") val retailPriceCheck: Double,
    @SerializedName("bulk_price_cash") val bulkPriceCash: Double?,
    @SerializedName("bulk_price_check") val bulkPriceCheck: Double?,
    @SerializedName("stock_quantity") val stockQuantity: Int?,
    @SerializedName("in_stock") val inStock: Boolean = true,
    @SerializedName("brand") val brand: Brand?,
    @SerializedName("category") val category: Category?,
    @SerializedName("discount_percent") val discountPercent: Int = 0,
    @SerializedName("technical_specs") val technicalSpecs: Map<String, String>? = null,
    @SerializedName("dimensions") val dimensions: Map<String, String>? = null,
    @SerializedName("compatible_models") val compatibleModels: List<String>? = null,
    @SerializedName("tags") val tags: List<String>? = null,
    @SerializedName("min_order_quantity") val minOrderQuantity: Int = 1,
    @SerializedName("weight_kg") val weightKg: Double? = null
)

data class Brand(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_fa") val nameFa: String?,
    @SerializedName("logo") val logo: String?
)

data class Category(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("name_en") val nameEn: String?,
    @SerializedName("image") val image: String?,
    @SerializedName("parent_id") val parentId: Int?,
    @SerializedName("children") val children: List<Category>?
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

data class Order(
    @SerializedName("id") val id: Int,
    @SerializedName("order_number") val orderNumber: String,
    @SerializedName("status") val status: String,
    @SerializedName("total_amount") val totalAmount: Double,
    @SerializedName("payment_type") val paymentType: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("items") val items: List<CartItem>?
)

data class CreateOrderRequest(
    @SerializedName("payment_type") val paymentType: String,
    @SerializedName("customer_notes") val customerNotes: String? = null
)

data class Banner(
    @SerializedName("id") val id: Int,
    @SerializedName("title") val title: String?,
    @SerializedName("image") val image: String,
    @SerializedName("link") val link: String?,
    @SerializedName("order") val order: Int
)

data class Reward(
    @SerializedName("id") val id: Int,
    @SerializedName("title") val title: String,
    @SerializedName("description") val description: String?,
    @SerializedName("image") val image: String?,
    @SerializedName("points_required") val pointsRequired: Int,
    @SerializedName("available_quantity") val availableQuantity: Int
)

data class CompanyInfo(
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String?,
    @SerializedName("logo") val logo: String?,
    @SerializedName("phones") val phones: List<String>?,
    @SerializedName("address") val address: String?,
    @SerializedName("working_hours") val workingHours: String?
)

// Home Screen Sections
data class HomeSection(
    @SerializedName("id") val id: Int,
    @SerializedName("type") val type: String, // bestselling, discounted, new, special
    @SerializedName("title") val title: String,
    @SerializedName("icon") val icon: String?,
    @SerializedName("enabled") val enabled: Boolean = true,
    @SerializedName("order") val order: Int,
    @SerializedName("limit") val limit: Int = 10
)

data class HomeSectionsResponse(
    @SerializedName("sections") val sections: List<HomeSection>
)

data class BannersResponse(
    @SerializedName("banners") val banners: List<Banner>
)

// Contact and About Settings
data class ContactInfo(
    @SerializedName("phone") val phone: String?,
    @SerializedName("email") val email: String?,
    @SerializedName("address") val address: String?,
    @SerializedName("working_hours") val workingHours: String?,
    @SerializedName("map_url") val mapUrl: String?
)

data class AboutInfo(
    @SerializedName("logo") val logo: String?,
    @SerializedName("history") val history: String?,
    @SerializedName("mission") val mission: String?,
    @SerializedName("vision") val vision: String?,
    @SerializedName("team") val team: String?,
    @SerializedName("achievements") val achievements: String?
)

