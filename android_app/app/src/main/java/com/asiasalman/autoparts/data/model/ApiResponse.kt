package com.asiasalman.autoparts.data.model

data class ApiResponse<T>(
    val success: Boolean,
    val message: String?,
    val data: T?
)

data class Pagination(
    val page: Int,
    val perPage: Int,
    val total: Int,
    val pages: Int,
    val hasNext: Boolean,
    val hasPrev: Boolean
)

data class ProductsResponse(
    val products: List<Product>,
    val pagination: Pagination
)

data class AuthResponse(
    val accessToken: String,
    val refreshToken: String,
    val user: User,
    val expiresIn: Int
)

